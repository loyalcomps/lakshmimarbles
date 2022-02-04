# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.tools import float_is_zero
from odoo.exceptions import UserError

import odoo.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    scheme_discount_amount = fields.Float(string="Scheme Discount(amt)", default=0.0)
    scheme_discount = fields.Float(string='Scheme Discount (%)', digits=dp.get_precision('Discount'),
                                   default=0.0)



    @api.onchange('scheme_discount_amount', 'scheme_discount', )
    def _onchange_scheme_discount(self):
        if self.invoice_id.type in ['in_invoice']:
            base_price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)

            if self.scheme_discount > 100:
                raise UserError(('Cannot give discount more than 100%.'))

            if self.scheme_discount_amount > base_price:
                raise UserError(('Cannot give discount more than cost price.'))

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'scheme_discount_amount', 'scheme_discount')
    def _compute_price(self):
        res = super(AccountInvoiceLine, self)._compute_price()
        currency = self.invoice_id and self.invoice_id.currency_id or None
        if self.invoice_id.type == 'in_invoice':
            base_price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            disc_amt = self.scheme_discount_amount/self.quantity

            disc_per = (base_price * self.scheme_discount) / 100
            price = base_price - disc_per-disc_amt
        else:
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)

        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(
                price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    def _set_taxes(self):
        res = super(AccountInvoiceLine, self)._set_taxes()
        if self.invoice_id.type in ('in_invoice'):
            self.price_unit = 0

    @api.depends('product_id')
    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.invoice_id.invoice_line_ids:
                line_rec.sl_no = line_num
                line_num += 1

    # @api.depends('price_subtotal_taxinc','quantity','invoice_id.freight_pdct')
    # def get_landing_cost(self):
    #
    #     for line in self:
    #         landing_cost = 0
    #         if line.quantity != 0:
    #             landing_cost = line.price_subtotal_taxinc/line.quantity
    #         line.landing_cost=landing_cost+line.invoice_id.freight_pdct

    # @api.depends('price_subtotal','quantity','invoice_id.freight_pdct')
    # def get_landing_cost(self):
    #
    #     for line in self:
    #         landing_cost = 0
    #         if line.quantity != 0:
    #             landing_cost = line.price_subtotal/line.quantity
    #         line.landing_cost=landing_cost+line.invoice_id.freight_pdct




    # @api.depends('price_subtotal_taxinc', 'quantity','invoice_id.freight_pdct')
    # def get_landing_cost(self):
		# for line in self:
		# 	landing_cost = line.price_subtotal_taxinc / line.quantity
		# 	line.landing_cost = landing_cost+line.invoice_id.freight_pdct

    @api.depends('price_unit','quantity')
    def calculate_gross_amt(self):
        for line in self:
            line.gross_amt = line.price_unit*line.quantity

    brand_id = fields.Many2one('product.brand', string="Brand",)
    category_id = fields.Many2one('product.category', string="Category")
    hsn = fields.Char(string="HSN/SAC")
    spcl_disc = fields.Float(string='Special Discount(amt)', compute='calculate_calc_residual', store=True, default=0.0)
    discount_amount = fields.Float(string="Discount(amt)", default=0.0)
    customer_tax_id = fields.Many2many('account.tax', string='Customer Taxes', required=True,
                                       domain=['|', ('active', '=', False), ('active', '=', True)])

    date_exp = fields.Date(string="Expiry Date")
    product_mrp = fields.Float(string="MRP", )
    sl_no = fields.Integer(compute='_get_line_numbers', string='Sl No.', readonly=False, store=True)
    landing_cost = fields.Float(string="Landing Cost", compute="get_landing_cost", store=True)
    barcode = fields.Char(string='Barcode')
    gross_amt = fields.Float(string = 'Gross Amount',compute='calculate_gross_amt',store= True)
    @api.depends('price_unit')
    @api.onchange('discount_amount', 'price_unit', 'quantity')
    def onchange_discount_amt(self):
        if self.price_unit and self.quantity != 0:
            self.discount = (self.discount_amount * 100) / (self.price_unit * self.quantity)

    @api.depends('price_unit')
    @api.onchange('discount', 'price_unit', 'quantity')
    def onchange_discount(self):
        if self.price_unit and self.quantity != 0:
            self.discount_amount = (self.discount * self.price_unit * self.quantity) / 100

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity', 'product_id', 'invoice_id.currency_id',
                 'invoice_id.partner_id', 'invoice_id.company_id', 'invoice_id.discount')
    def calculate_calc_residual(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        #         if self.invoice_id.type in ['in_refund']:
        #             return
        spl_dis = 0.0
        if self.invoice_id.type in ['in_invoice']:
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,

                                                          partner=self.invoice_id.partner_id)
            included_amount = taxes['total_included']
            if self.invoice_id.discount_type == "percent":
                included_amount = ((included_amount * self.invoice_id.discount) / 100)
            if self.invoice_id.discount_type == "amount":
                total_amount = 0
                # finding total taxed amount
                for line in self.invoice_id.invoice_line_ids:
                    price_taxed = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

                    amt_taxes = line.invoice_line_tax_ids.compute_all(price_taxed, currency, line.quantity,
                                                                      product=line.product_id,

                                                                      partner=line.invoice_id.partner_id)
                    total_amount += amt_taxes['total_included']
                if total_amount != 0:
                    spl_dis = (included_amount * self.invoice_id.discount / total_amount)
            self.spcl_disc = spl_dis

    @api.onchange('product_mrp')
    def onchange_check(self):

        if self.product_mrp != 0:
            if self.product_mrp < self.landing_cost:
                raise UserError(('Cannot give MRP less than landing cost.'))

    @api.model
    def create(self, vals):

        if vals['product_id'] :

            product_id = self.env['product.product'].search([('id', '=', vals['product_id'])])

            if 'hsn' in vals:
                product_id.hsn = vals['hsn']
            if 'invoice_line_tax_ids' in vals:
                product_id.supplier_taxes_id = vals['invoice_line_tax_ids']
            if 'customer_tax_id' in vals:
                product_id.taxes_id = vals['customer_tax_id']

            if 'date_exp' in vals:
                product_id.date_exp = vals['date_exp']
            # if 'product_mrp' in vals:
            #     product_id.product_mrp = vals['product_mrp']
            if 'brand_id' in vals:
                product_id.brand_id = vals['brand_id']
            if 'category_id' in vals:
                product_id.categ_id = vals['category_id']
            if 'barcode' in vals:
                product_id.barcode = vals['barcode']
            product_id.available_in_pos = True



        return super(AccountInvoiceLine, self).create(vals)

    @api.multi
    def write(self, vals):

        if self.product_id:
            product_id = self.env['product.product'].search([('id', '=', self.product_id.id)])
            if 'hsn' in vals:
                product_id.hsn = vals['hsn']
            if 'invoice_line_tax_ids' in vals:
                product_id.supplier_taxes_id = vals['invoice_line_tax_ids']
            if 'customer_tax_id' in vals:
                product_id.taxes_id = vals['customer_tax_id']

            if 'date_exp' in vals:
                product_id.date_exp = vals['date_exp']
            # if 'product_mrp' in vals:
            #     product_id.product_mrp = vals['product_mrp']
            if 'brand_id' in vals:
                product_id.brand_id = vals['brand_id']
            if 'category_id' in vals:
                product_id.categ_id = vals['category_id']
            if 'barcode' in vals:
                product_id.barcode = vals['barcode']
            product_id.available_in_pos = True


        return super(AccountInvoiceLine, self).write(vals)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res=super(AccountInvoiceLine, self)._onchange_product_id()

        self.hsn = self.product_id.hsn

        self.customer_tax_id = self.product_id.taxes_id
        self.product_mrp = self.product_id.product_mrp
        self.barcode = self.product_id.barcode
        self.brand_id = self.product_id.brand_id
        self.category_id = self.product_id.categ_id
        self.date_exp = self.product_id.date_exp

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    _sql_constraints = [
        ('reference_uniq', 'unique(reference, partner_id,type)', 'Reference Number must be unique per Partner!'),
    ]

    discount = fields.Float(string="Discount", digits=dp.get_precision('Discount'), default=0.0)
    discount_type = fields.Selection([('percent', "Percentage"), ('amount', "Amount")], string="Discount type")
    amount_discount = fields.Monetary(string="Discount", store=True, readonly=True, track_visibility='always',
                                      compute="_compute_amount")
    discount_amt = fields.Float(string="Discount", digits=dp.get_precision('Discount'), default=0.0, store=True)
    round_off_value = fields.Float(string="Round Off",default=0.0)
    round_off_operation = fields.Selection([('plus','+'),('minus','-')],string='Round Off Operation')
    rounded_total = fields.Float(compute='_compute_amount', string='Rounded Value',default=0.0)
    freight = fields.Float(string="Freight Charge", digits=dp.get_precision('Discount'), default=0.0)
    amount_freight = fields.Monetary(string="Freight Rate", store=True, readonly=True, track_visibility='always',
                                     compute="_compute_amount")
    freight_pdct = fields.Float(string="Freight Charge", default=0.0)
    amount_scheme_discount = fields.Monetary(string="Scheme Discount", store=True, readonly=True, track_visibility='always',
                                             compute="_compute_amount")

    @api.multi
    def action_invoice_open(self):
        super(AccountInvoice, self).action_invoice_open()

        for record in self:
            if record.type == 'in_invoice':

                for line in record.invoice_line_ids:
                    line.product_id.landing_cost = line.landing_cost

    @api.onchange('freight' )
    def _onchange_freight(self):
        qty =0
        if self.type in ['in_invoice']:
            for line in self.invoice_line_ids:
                qty+=line.quantity
            if qty != 0:
                self.freight_pdct = self.freight/qty


    @api.onchange('discount_type', 'discount', )
    def _onchange_discount(self):
        if self.type in ['in_invoice']:
            disc_amount = 0
            if self.discount_type == "amount":
                if self.discount >= self.amount_untaxed + self.amount_tax:
                    raise UserError(('Cannot give discount more than total amount.'))
                self.discount_amt = self.discount
            if self.discount_type == "percent":
                disc_amount = ((self.amount_untaxed + self.amount_tax) * self.discount) / 100
                if disc_amount >= self.amount_untaxed + self.amount_tax:
                    raise UserError(('Cannot give discount more than total amount.'))
                self.discount_amt = disc_amount

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'discount','type','round_off_value','round_off_operation','freight')
    def _compute_amount(self):

        res = super(AccountInvoice, self)._compute_amount()
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)


        if self.type in ['in_invoice', 'in_refund']:

            self.amount_total = self.amount_untaxed + self.amount_tax - self.discount_amt+self.freight
            for line in self.invoice_line_ids:
                base_price = line.price_unit * line.quantity * (1 - (line.discount or 0.0) / 100.0)
                self.amount_scheme_discount += line.scheme_discount_amount
                self.amount_scheme_discount += (base_price * line.scheme_discount) / 100
                self.amount_discount += (line.price_unit * line.quantity * line.discount) / 100
            self.amount_discount += self.discount_amt
            self.amount_freight = self.freight
        else:
            self.amount_total = self.amount_untaxed + self.amount_tax
        if self.round_off_operation == 'plus':
            self.amount_total = self.amount_total+self.round_off_value
            self.rounded_total = self.round_off_value
        elif self.round_off_operation == 'minus':
            self.amount_total = self.amount_total-self.round_off_value
            self.rounded_total = self.round_off_value*-1
        else:
            self.amount_total = self.amount_total

        amount_total_company_signed = self.amount_total

        if self.currency_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)

        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign





    @api.onchange('purchase_id')
    def purchase_order_change(self):

        if not self.purchase_id:
            return {}
        if not self.discount:
            self.discount = self.purchase_id.discount
        if not self.discount_type:
            self.discount_type = self.purchase_id.discount_type
        if not self.discount_amt:
            self.discount_amt = self.purchase_id.discount_amt
        res = super(AccountInvoice, self).purchase_order_change()

    @api.multi
    def action_move_create(self):

        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:

            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(
                    total, date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    if self.round_off_value != 0.0 and self.type == 'in_invoice':
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1] - self.rounded_total+self.discount_amt-self.expense,
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        ir_values = self.env['ir.values']
                        if self.round_off_operation == 'plus':
                            acc_id = ir_values.get_default('account.config.settings', 'round_off_account_expense')
                        if self.round_off_operation == 'minus':
                            acc_id = ir_values.get_default('account.config.settings', 'round_off_account_income')

                        iml.append({
                            'type': 'dest',
                            'name': "Round off",
                            'price': self.rounded_total,
                            'account_id': acc_id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })

                        if self.discount_amt!= 0.0:
                            disc_id = ir_values.get_default('account.config.settings', 'discount_account')
                            iml.append({
                                'type': 'dest',
                                'name': "Purchase Discount",
                                'price': -self.discount_amt,
                                'account_id': disc_id,
                                'date_maturity': t[0],
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                        for line in self.purchase_expense_line_ids:
                            if line.name=='freight':
                                disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                                iml.append({
                                    'type': 'dest',
                                    'name': "Purchase Freight Charge",
                                    'price': line.rate,
                                    'account_id': disc_id,
                                    'date_maturity': t[0],
                                    'amount_currency': diff_currency and amount_currency,
                                    'currency_id': diff_currency and inv.currency_id.id,
                                    'invoice_id': inv.id
                                })
                            if line.name=='union':
                                disc_id = ir_values.get_default('account.config.settings', 'union_account')
                                iml.append({
                                    'type': 'dest',
                                    'name': "Purchase Union Charge",
                                    'price': line.rate,
                                    'account_id': disc_id,
                                    'date_maturity': t[0],
                                    'amount_currency': diff_currency and amount_currency,
                                    'currency_id': diff_currency and inv.currency_id.id,
                                    'invoice_id': inv.id
                                })

                            if line.name=='packing':
                                disc_id = ir_values.get_default('account.config.settings', 'packing_account')
                                iml.append({
                                    'type': 'dest',
                                    'name': "Purchase Packing Charge",
                                    'price': line.rate,
                                    'account_id': disc_id,
                                    'date_maturity': t[0],
                                    'amount_currency': diff_currency and amount_currency,
                                    'currency_id': diff_currency and inv.currency_id.id,
                                    'invoice_id': inv.id
                                })
                            if line.name=='other':
                                disc_id = ir_values.get_default('account.config.settings', 'other_account')
                                iml.append({
                                    'type': 'dest',
                                    'name': "Purchase Other Charges",
                                    'price': line.rate,
                                    'account_id': disc_id,
                                    'date_maturity': t[0],
                                    'amount_currency': diff_currency and amount_currency,
                                    'currency_id': diff_currency and inv.currency_id.id,
                                    'invoice_id': inv.id
                                })
                        # Other Purchase Expense
                        # if self.expense!= 0.0:
                        #     disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                        #     iml.append({
                        #         'type': 'dest',
                        #         'name': "Other Purchase Expense",
                        #         'price': self.expense,
                        #         'account_id': disc_id,
                        #         'date_maturity': t[0],
                        #         'amount_currency': diff_currency and amount_currency,
                        #         'currency_id': diff_currency and inv.currency_id.id,
                        #         'invoice_id': inv.id
                        #     })

                        # # freight
                        # if self.freight != 0.0:
                        #     disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                        #     iml.append({
                        #         'type': 'dest',
                        #         'name': "Purchase Union Charge",
                        #         'price': self.freight,
                        #         'account_id': disc_id,
                        #         'date_maturity': t[0],
                        #         'amount_currency': diff_currency and amount_currency,
                        #         'currency_id': diff_currency and inv.currency_id.id,
                        #         'invoice_id': inv.id
                        #     })
                    else:

                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1]+self.discount_amt-self.expense,
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        if self.discount_amt!= 0.0:
                            ir_values = self.env['ir.values']
                            disc_id = ir_values.get_default('account.config.settings', 'discount_account')
                            iml.append({
                                'type': 'dest',
                                'name': "Purchase Discount",
                                'price': -self.discount_amt,
                                'account_id': disc_id,
                                'date_maturity': t[0],
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })

                        # if self.expense!= 0.0:
                        #     ir_values = self.env['ir.values']
                        #     disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                        #     iml.append({
                        #         'type': 'dest',
                        #         'name': "Other Purchase Expense",
                        #         'price': self.expense,
                        #         'account_id': disc_id,
                        #         'date_maturity': t[0],
                        #         'amount_currency': diff_currency and amount_currency,
                        #         'currency_id': diff_currency and inv.currency_id.id,
                        #         'invoice_id': inv.id
                        #     })

                        for line in self.purchase_expense_line_ids:
                            ir_values = self.env['ir.values']
                            if line.name == 'freight':
                                disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                                iml.append({
                                    'type': 'dest',
                                    'name': "Purchase Freight Charge",
                                    'price': line.rate,
                                    'account_id': disc_id,
                                    'date_maturity': t[0],
                                    'amount_currency': diff_currency and amount_currency,
                                    'currency_id': diff_currency and inv.currency_id.id,
                                    'invoice_id': inv.id
                                })
                            if line.name == 'union':
                                disc_id = ir_values.get_default('account.config.settings', 'union_account')
                                iml.append({
                                    'type': 'dest',
                                    'name': "Purchase Union Charge",
                                    'price': line.rate,
                                    'account_id': disc_id,
                                    'date_maturity': t[0],
                                    'amount_currency': diff_currency and amount_currency,
                                    'currency_id': diff_currency and inv.currency_id.id,
                                    'invoice_id': inv.id
                                })

                            if line.name == 'packing':
                                disc_id = ir_values.get_default('account.config.settings', 'packing_account')
                                iml.append({
                                    'type': 'dest',
                                    'name': "Purchase Packing Charge",
                                    'price': line.rate,
                                    'account_id': disc_id,
                                    'date_maturity': t[0],
                                    'amount_currency': diff_currency and amount_currency,
                                    'currency_id': diff_currency and inv.currency_id.id,
                                    'invoice_id': inv.id
                                })
                            if line.name == 'other':
                                disc_id = ir_values.get_default('account.config.settings', 'other_account')
                                iml.append({
                                    'type': 'dest',
                                    'name': "Purchase Other Charges",
                                    'price': line.rate,
                                    'account_id': disc_id,
                                    'date_maturity': t[0],
                                    'amount_currency': diff_currency and amount_currency,
                                    'currency_id': diff_currency and inv.currency_id.id,
                                    'invoice_id': inv.id
                                })


            else:
                if self.round_off_value != 0.0 and self.type == 'in_invoice':
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total - self.rounded_total+self.discount_amt-self.expense,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                    ir_values = self.env['ir.values']
                    if self.round_off_operation == 'plus':
                        acc_id = ir_values.get_default('account.config.settings', 'round_off_account_expense')
                    if self.round_off_operation == 'minus':
                        acc_id = ir_values.get_default('account.config.settings', 'round_off_account_income')
                    iml.append({
                        'type': 'dest',
                        'name': "Round off",
                        'price': self.rounded_total,
                        'account_id': acc_id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                    if self.discount_amt != 0.0:
                        disc_id = ir_values.get_default('account.config.settings', 'discount_account')
                        iml.append({
                            'type': 'dest',
                            'name': "Purchase Discount",
                            'price': -self.discount_amt,
                            'account_id': disc_id,
                            'date_maturity': inv.date_due,
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                    for line in self.purchase_expense_line_ids:
                        if line.name == 'freight':
                            disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                            iml.append({
                                'type': 'dest',
                                'name': "Purchase Freight Charge",
                                'price': line.rate,
                                'account_id': disc_id,
                                'date_maturity': inv.date_due,
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                        if line.name == 'union':
                            disc_id = ir_values.get_default('account.config.settings', 'union_account')
                            iml.append({
                                'type': 'dest',
                                'name': "Purchase Union Charge",
                                'price': line.rate,
                                'account_id': disc_id,
                                'date_maturity': inv.date_due,
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                        if line.name == 'packing':
                            disc_id = ir_values.get_default('account.config.settings', 'packing_account')
                            iml.append({
                                'type': 'dest',
                                'name': "Purchase Packing Charge",
                                'price': line.rate,
                                'account_id': disc_id,
                                'date_maturity': inv.date_due,
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                        if line.name == 'other':
                            disc_id = ir_values.get_default('account.config.settings', 'other_account')
                            iml.append({
                                'type': 'dest',
                                'name': "Purchase Other Charge",
                                'price': line.rate,
                                'account_id': disc_id,
                                'date_maturity': inv.date_due,
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })



                    # if self.expense != 0.0:
                    #     disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                    #     iml.append({
                    #         'type': 'dest',
                    #         'name': "Other Purchase Expense",
                    #         'price': self.expense,
                    #         'account_id': disc_id,
                    #         'date_maturity': inv.date_due,
                    #         'amount_currency': diff_currency and amount_currency,
                    #         'currency_id': diff_currency and inv.currency_id.id,
                    #         'invoice_id': inv.id
                    #     })
                else:
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total+self.discount_amt-self.expense,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                    if self.discount_amt != 0.0:
                        ir_values = self.env['ir.values']
                        disc_id = ir_values.get_default('account.config.settings', 'discount_account')
                        iml.append({
                            'type': 'dest',
                            'name': "Purchase Discount",
                            'price': -self.discount_amt,
                            'account_id': disc_id,
                            'date_maturity': inv.date_due,
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                    # if self.expense != 0.0:
                    #     ir_values = self.env['ir.values']
                    #     disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                    #     iml.append({
                    #         'type': 'dest',
                    #         'name': "Other Purchase Expense",
                    #         'price': self.expense,
                    #         'account_id': disc_id,
                    #         'date_maturity': inv.date_due,
                    #         'amount_currency': diff_currency and amount_currency,
                    #         'currency_id': diff_currency and inv.currency_id.id,
                    #         'invoice_id': inv.id
                    #     })

                    for line in self.purchase_expense_line_ids:
                        ir_values = self.env['ir.values']
                        if line.name == 'freight':
                            disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                            iml.append({
                                'type': 'dest',
                                'name': "Purchase Freight Charge",
                                'price': line.rate,
                                'account_id': disc_id,
                                'date_maturity': inv.date_due,
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                        if line.name == 'union':
                            disc_id = ir_values.get_default('account.config.settings', 'union_account')
                            iml.append({
                                'type': 'dest',
                                'name': "Purchase Union Charge",
                                'price': line.rate,
                                'account_id': disc_id,
                                'date_maturity': inv.date_due,
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                        if line.name == 'packing':
                            disc_id = ir_values.get_default('account.config.settings', 'packing_account')
                            iml.append({
                                'type': 'dest',
                                'name': "Purchase Packing Charge",
                                'price': line.rate,
                                'account_id': disc_id,
                                'date_maturity': inv.date_due,
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                        if line.name == 'other':
                            disc_id = ir_values.get_default('account.config.settings', 'other_account')
                            iml.append({
                                'type': 'dest',
                                'name': "Purchase Other Charge",
                                'price': line.rate,
                                'account_id': disc_id,
                                'date_maturity': inv.date_due,
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            res = super(AccountInvoice, self).action_move_create()
        return True

    # @api.onchange('reference')
    # def OnchangeReference(self):
    #     for invoice in self:
    #         if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
    #             if self.id:
    #                 if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference),
    #                                 ('company_id', '=', invoice.company_id.id),
    #                                 ('commercial_partner_id', '=', invoice.commercial_partner_id.id),
    #                                 ('id', '!=', invoice.id)]):
    #                     invoice.reference = False
    #                     raise UserError(_(
    #                         "Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))
    #             else:
    #                 if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference),
    #                             ('company_id', '=', invoice.company_id.id),
    #                             ('commercial_partner_id', '=', invoice.commercial_partner_id.id),
    #                             ]):
    #                     self.update({'reference' :False})
    #                     raise UserError(_(
    #                         "Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))


    # @api.model
    # def create(self, vals):
    #     # type=vals['type']
    #     reference = vals['reference']
    #     company_id = vals['company_id']
    #     commercial_partner_id=self.env['res.partner'].search([('id','=',vals['partner_id'])]).commercial_partner_id.id
    #
    #     if self.search([('type', '=', self.type), ('reference', '=',reference),
    #                         ('company_id', '=', company_id),
    #                         ('commercial_partner_id', '=', commercial_partner_id),
    #                         ]):
    #         raise UserError(_(
    #                 "Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))
    #
    #     count = 0
    #
    #
    #
    #     return super(AccountInvoice, self).create(vals)
