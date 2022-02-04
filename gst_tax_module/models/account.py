# -*- coding: utf-8 -*-

import math

from odoo import models, fields, api,_
from odoo.tools import float_is_zero
from odoo.exceptions import UserError

import odoo.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

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

    @api.depends('price_subtotal_taxinc','quantity','invoice_id.freight_pdct','product_id')
    def get_landing_cost(self):

        for line in self:
            landing_cost = 0
            if line.quantity != 0:
                landing_cost = line.price_subtotal_taxinc/line.quantity
            line.landing_cost=landing_cost+line.invoice_id.freight_pdct


    @api.depends('price_unit','quantity')
    def calculate_gross_amt(self):
        for line in self:
            line.gross_amt = line.price_unit*line.quantity

    brand_id = fields.Many2one('product.brand', string="Brand",)
    category_id = fields.Many2one('product.category', string="Category")
    hsn = fields.Char(string="HSN/SAC")
    spcl_disc = fields.Float(string='Special Discount(amt)', compute='calculate_calc_residual', store=True, default=0.0)
    discount_amount = fields.Float(string="Discount(amt)", default=0.0)
    sale_price = fields.Float(string="Sale Price", default=0.0)
    customer_tax_id = fields.Many2many('account.tax', string='Customer Taxes', required=True,
                                       domain=['|', ('active', '=', False), ('active', '=', True)])

    sl_no = fields.Integer(compute='_get_line_numbers', string='Sl No.', readonly=False, store=True)
    landing_cost = fields.Float(string="Landing Cost", compute="get_landing_cost", store=True)
    barcode = fields.Char(string='Barcode')
    gross_amt = fields.Float(string = 'Gross Amount',compute='calculate_gross_amt',store= True)

    price_subtotal_tax = fields.Float(compute='_compute_price_tax', string='Taxable Value',
                                      digits=dp.get_precision('Product Price'), store=True)
    price_subtotal_taxinc = fields.Float(compute='_compute_price_tax', string=' Total',
                                         digits=dp.get_precision('Product Price'), store=True)

    price_unit_tax = fields.Float(compute='_compute_price_tax', string='Unit Price(Exc)',
                                  digits=dp.get_precision('Product Price'), store=True)

    inclusive = fields.Boolean('inclusive', default=False, related='invoice_id.inclusive')

    date_exp = fields.Integer( string="Best Before", help="Expiry date", copy=False)

    # expiry_date = fields.Date(string='Expiry date', help="Expiry date", copy=False)


    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'inclusive')
    def _compute_price(self):
        res = super(AccountInvoiceLine, self)._compute_price()
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            if self.invoice_id.inclusive:
                taxes = self.invoice_line_tax_ids.with_context(price_include=True,include_base_amount=True).compute_all_inc(price, currency,
                                                                                               self.quantity,
                                                                                               product=self.product_id,
                                                                                               partner=self.invoice_id.partner_id)
            else:
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                              partner=self.invoice_id.partner_id)

        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(
                price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign


    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id','inclusive')
    def _compute_price_tax(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        prec = currency.decimal_places
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        q = 1
        unit_taxes = False
        taxes = False
        if self.invoice_line_tax_ids:
            if self.invoice_id.inclusive:
                unit_taxes = self.invoice_line_tax_ids.with_context(price_include=True,include_base_amount=True).compute_all_inc(price, currency, q, product=self.product_id,
                                                                   partner=self.invoice_id.partner_id)
                taxes = self.invoice_line_tax_ids.with_context(price_include=True,include_base_amount=True).compute_all_inc(price, currency, q, product=self.product_id,
                                                           partner=self.invoice_id.partner_id)
            else:
                unit_taxes = self.invoice_line_tax_ids.compute_all(price, currency, q, product=self.product_id,
                                                                   partner=self.invoice_id.partner_id)
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                      partner=self.invoice_id.partner_id)

        self.price_unit_tax = unit_taxes['total_excluded'] if unit_taxes else  price
        self.price_subtotal_tax = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_subtotal_taxinc = taxes['total_included'] if taxes else self.quantity * price
        if self.invoice_id:
            self.price_subtotal_tax = round(self.price_subtotal_tax, prec)
            self.price_subtotal_taxinc = round(self.price_subtotal_taxinc, prec)
            self.price_unit_tax = self.invoice_id.currency_id.round(self.price_unit_tax)

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
                 'invoice_id.partner_id', 'invoice_id.company_id', 'invoice_id.discount','inclusive')
    def calculate_calc_residual(self):

        currency = self.invoice_id and self.invoice_id.currency_id or None
        spl_dis = 0.0
        if self.invoice_id.type in ['in_invoice']:
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            if self.invoice_id.inclusive:
                taxes = self.invoice_line_tax_ids.with_context(price_include=True,
                                                                       include_base_amount=True).compute_all_inc(price, currency, self.quantity, product=self.product_id,
                                                              partner=self.invoice_id.partner_id)
            else:
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,partner=self.invoice_id.partner_id)
            included_amount = taxes['total_included']
            if self.invoice_id.discount_type == "percent":
                included_amount = ((included_amount * self.invoice_id.discount) / 100)
            if self.invoice_id.discount_type == "amount":
                total_amount = 0
                for line in self.invoice_id.invoice_line_ids:
                    price_taxed = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

                    if self.invoice_id.inclusive:
                        amt_taxes = line.invoice_line_tax_ids.with_context(price_include=True,
                                                                       include_base_amount=True).compute_all_inc(price_taxed, currency, line.quantity,
                                                                          product=line.product_id,
                                                                          partner=line.invoice_id.partner_id)
                    else:

                        amt_taxes = line.invoice_line_tax_ids.compute_all(price_taxed, currency, line.quantity,
                                                                      product=line.product_id,

                                                                      partner=line.invoice_id.partner_id)
                    total_amount += amt_taxes['total_included']
                if total_amount != 0:
                    spl_dis = (included_amount * self.invoice_id.discount / total_amount)
            self.spcl_disc = spl_dis

    # @api.onchange('product_mrp')
    # def onchange_check(self):
    #
    #     if self.product_mrp != 0:
    #         if self.product_mrp < self.landing_cost:
    #             raise UserError(('Cannot give MRP less than landing cost.'))

    # @api.model
    # def create(self, vals):

    #     if vals['product_id'] :

    #         product_id = self.env['product.product'].search([('id', '=', vals['product_id'])])
    #         if 'hsn' in vals:
    #             product_id.hsn = vals['hsn']
    #         if 'invoice_line_tax_ids' in vals:
    #             product_id.supplier_taxes_id = vals['invoice_line_tax_ids']
    #         if 'customer_tax_id' in vals:
    #             product_id.taxes_id = vals['customer_tax_id']
    #         if 'brand_id' in vals:
    #             product_id.brand_id = vals['brand_id']
    #         if 'category_id' in vals:
    #             if vals['category_id'] :
    #                 product_id.categ_id = vals['category_id']
    #         if 'barcode' in vals:
    #             product_id.barcode = vals['barcode']
    #         if 'date_exp' in vals:
    #             product_id.expiry_date = vals['date_exp']
    #         if 'sale_price' in vals:
    #             product_id.lst_price = vals['sale_price']

    #         product_id.available_in_pos = True

    #     return super(AccountInvoiceLine, self).create(vals)

    # @api.multi
    # def write(self, vals):

    #     if self.product_id:
    #         product_id = self.env['product.product'].search([('id', '=', self.product_id.id)])
    #         if 'hsn' in vals:
    #             product_id.hsn = vals['hsn']
    #         if 'invoice_line_tax_ids' in vals:
    #             product_id.supplier_taxes_id = vals['invoice_line_tax_ids']
    #         if 'customer_tax_id' in vals:
    #             product_id.taxes_id = vals['customer_tax_id']
    #         if 'brand_id' in vals:
    #             product_id.brand_id = vals['brand_id']
    #         if 'category_id' in vals:
    #             if vals['category_id']:
    #                 product_id.categ_id = vals['category_id']
    #         if 'barcode' in vals:
    #             product_id.barcode = vals['barcode']
    #         if 'date_exp' in vals:
    #             product_id.expiry_date = vals['date_exp']
    #         if 'sale_price' in vals:
    #             product_id.lst_price = vals['sale_price']
    #         product_id.available_in_pos = True

    #     return super(AccountInvoiceLine, self).write(vals)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res=super(AccountInvoiceLine, self)._onchange_product_id()

        self.hsn = self.product_id.hsn
        self.customer_tax_id = self.product_id.taxes_id

        self.barcode = self.product_id.barcode
        self.brand_id = self.product_id.brand_id
        self.category_id = self.product_id.categ_id
        self.sale_price = self.product_id.lst_price


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    discount = fields.Float(string="Discount", digits=dp.get_precision('Discount'), default=0.0)
    discount_type = fields.Selection([('percent', "Percentage"), ('amount', "Amount")], string="Discount type")
    amount_discount = fields.Monetary(string="Discount", store=True, readonly=True, track_visibility='always',
                                      compute="_compute_amount")
    discount_amt = fields.Float(string="Discount", digits=dp.get_precision('Discount'), default=0.0, store=True)
    round_off_value_purchase = fields.Float(string="Round Off",default=0.0)
    round_off_operation = fields.Selection([('plus','+'),('minus','-')],string='Round Off Operation',default='plus')
    rounded_total_purchase = fields.Float(compute='_compute_amount', string='Rounded Value',default=0.0)
    freight = fields.Float(string="Freight Charge", digits=dp.get_precision('Discount'), default=0.0)
    amount_freight = fields.Monetary(string="Freight Rate", store=True, readonly=True, track_visibility='always',
                                     compute="_compute_amount")
    freight_pdct = fields.Float(string="Freight Charge", default=0.0)

    inclusive = fields.Boolean('inclusive', default=False)

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
                 'discount','type','round_off_value_purchase','round_off_operation','freight','inclusive')
    def _compute_amount(self):

        res = super(AccountInvoice, self)._compute_amount()
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        # sale - round off
        self.rounded_total = round(self.amount_untaxed + self.amount_tax)
        #

        if self.type in ['in_invoice', 'in_refund']:

            self.amount_total = self.amount_untaxed + self.amount_tax - self.discount_amt+self.freight
            for line in self.invoice_line_ids:
                self.amount_discount += (line.price_unit * line.quantity * line.discount) / 100
            self.amount_discount += self.discount_amt
            self.amount_freight = self.freight
        else:
            self.amount_total = self.amount_untaxed + self.amount_tax
        # sale - round off value
        self.round_off_value = self.rounded_total - (self.amount_untaxed + self.amount_tax)
        #
        if self.round_off_operation == 'plus':
            self.amount_total = self.amount_total+self.round_off_value_purchase
            self.rounded_total_purchase = self.round_off_value_purchase
        elif self.round_off_operation == 'minus':
            self.amount_total = self.amount_total-self.round_off_value_purchase
            self.rounded_total_purchase = self.round_off_value_purchase*-1
        else:
            self.amount_total = self.amount_total

        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
        self.amount_tax=self.amount_tax

    # @api.multi
    # def get_taxes_values(self):
    #     res = super(AccountInvoice, self).get_taxes_values()
    #     tax_grouped = {}
    #     for line in self.invoice_line_ids:
    #         price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #
    #         if self.invoice_id.inclusive:
    #             taxes = line.invoice_line_tax_ids.with_context(price_include=True,include_base_amount=True).compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
    #                                                       self.partner_id)['taxes']
    #         else:
    #             taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
    #                                                       self.partner_id)['taxes']
    #         for tax in taxes:
    #             val = self._prepare_tax_line_vals(line, tax)
    #             key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
    #
    #             if key not in tax_grouped:
    #                 tax_grouped[key] = val
    #             else:
    #                 tax_grouped[key]['amount'] += val['amount']
    #                 tax_grouped[key]['base'] += val['base']
    #     return tax_grouped
    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self.sudo().move_id.line_ids:
            if line.account_id.internal_type in ('receivable', 'payable'):
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = (line.currency_id and line.currency_id.with_context(
                        date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
                    residual += from_currency.compute(line.amount_residual, self.currency_id)
        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        if self.round_active is True and self.type == 'out_invoice':
            self.residual = round(abs(residual))
        else:
            self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False


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
                    if self.type =='in_invoice':
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

                        if self.freight!= 0.0:
                            ir_values = self.env['ir.values']
                            disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                            iml.append({
                                'type': 'dest',
                                'name': "Purchase Freight Rate",
                                'price': self.freight,
                                'account_id': disc_id,
                                'date_maturity': t[0],
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })

                        if self.round_off_value_purchase != 0.0:
                            iml.append({
                                'type': 'dest',
                                'name': name,
                                'price': t[1] - self.rounded_total_purchase + self.discount_amt - self.freight,
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
                                'price': self.rounded_total_purchase,
                                'account_id': acc_id,
                                'date_maturity': t[0],
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                        else:
                            iml.append({
                                'type': 'dest',
                                'name': name,
                                'price': t[1] + self.discount_amt - self.freight,
                                'account_id': inv.account_id.id,
                                'date_maturity': t[0],
                                'amount_currency': diff_currency and amount_currency,
                                'currency_id': diff_currency and inv.currency_id.id,
                                'invoice_id': inv.id
                            })
                    elif self.round_active is True and self.type == 'out_invoice':
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1]+self.round_off_value,
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                        ir_values = self.env['ir.values']
                        acc_id = ir_values.get_default('account.config.settings', 'round_off_account')
                        iml.append({
                            'type': 'dest',
                            'name': "Round off",
                            'price': -self.round_off_value,
                            'account_id': acc_id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                    else:

                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1],
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })


            else:
                if self.type == 'in_invoice':
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
                    if self.freight != 0.0:
                        disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                        iml.append({
                            'type': 'dest',
                            'name': "Purchase Freight Rate",
                            'price': self.freight,
                            'account_id': disc_id,
                            'date_maturity': inv.date_due,
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                    if self.round_off_value_purchase != 0.0:
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': total - self.rounded_total_purchase + self.discount_amt - self.freight,
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
                            'price': self.rounded_total_purchase,
                            'account_id': acc_id,
                            'date_maturity': inv.date_due,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })

                    else:
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': total+self.discount_amt-self.freight,
                            'account_id': inv.account_id.id,
                            'date_maturity': inv.date_due,
                            'amount_currency': diff_currency and total_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                elif self.round_active is True and self.type == 'out_invoice':
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total + self.round_off_value,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                    ir_values = self.env['ir.values']
                    acc_id = ir_values.get_default('account.config.settings', 'round_off_account')
                    iml.append({
                        'type': 'dest',
                        'name': "Round off",
                        'price': -self.round_off_value,
                        'account_id': acc_id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                else:
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
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


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.multi
    def compute_all_inc(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):
        """ Returns all information required to apply taxes (in self + their children in case of a tax goup).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }]
        } """
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        prec = currency.decimal_places

        # In some cases, it is necessary to force/prevent the rounding of the tax and the total
        # amounts. For example, in SO/PO line, we don't want to round the price unit at the
        # precision of the currency.
        # The context key 'round' allows to force the standard behavior.
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5

        base_values = self.env.context.get('base_values')
        if not base_values:
            total_excluded = total_included = base = round(price_unit * quantity, prec)
        else:
            total_excluded, total_included, base = base_values

        # Sorting key is mandatory in this case. When no key is provided, sorted() will perform a
        # search. However, the search method is overridden in account.tax in order to add a domain
        # depending on the context. This domain might filter out some taxes from self, e.g. in the
        # case of group taxes.
        for tax in self.sorted(key=lambda r: r.sequence):
            if tax.amount_type == 'group':

                children = tax.children_tax_ids.with_context(base_values=(total_excluded, total_included, base))
                if 'include_base_amount' in self.env.context:
                    ret = children.with_context(price_include=True,include_base_amount=True).compute_all_inc(price_unit, currency, quantity, product, partner)
                else:
                    ret = children.compute_all_inc(price_unit, currency, quantity, product, partner)

                total_excluded = ret['total_excluded']
                if 'include_base_amount' in self.env.context:
                    base = ret['base']
                else:
                    base = ret['base'] if tax.include_base_amount else base
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue
            if 'price_include' in self.env.context:

                tax_amount = tax.with_context(price_include=True)._compute_amount_inc(base, price_unit, quantity, product, partner)
            else:
                tax_amount = tax._compute_amount_inc(base, price_unit, quantity, product,partner)
            if not round_tax:
                tax_amount = round(tax_amount, prec)
            else:
                tax_amount = currency.round(tax_amount)
            if 'price_include' in self.env.context:
                total_excluded -= tax_amount
                base -= tax_amount
            else:
                if tax.price_include:
                    total_excluded -= tax_amount
                    base -= tax_amount
                else:
                    total_included += tax_amount

            # Keep base amount used for the current tax
            tax_base = base
            if 'include_base_amount' in self.env.context:
                base += tax_amount
            else:
                if tax.include_base_amount:
                    base += tax_amount

            taxes.append({
                'id': tax.id,
                'name': tax.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': tax_amount,
                'base': tax_base,
                'sequence': tax.sequence,
                'account_id': tax.account_id.id,
                'refund_account_id': tax.refund_account_id.id,
                'analytic': tax.analytic,
            })

        # taxes = sorted(taxes, key=lambda k: k['sequence'])
        return {
            'taxes': sorted(taxes, key=lambda k: k['sequence']),
            'total_excluded': currency.round(total_excluded) if round_total else total_excluded,
            'total_included': currency.round(total_included) if round_total else total_included,
            'base': base,
        }

        # return super(AccountTax, self).compute_all(price_unit, currency, quantity, product, partner)


    def _compute_amount_inc(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        self.ensure_one()

        if 'price_include' in self.env.context:
            price_include = True
            if (self.amount_type == 'percent' and not price_include) or (
                    self.amount_type == 'division' and price_include):
                return base_amount * self.amount / 100
            if self.amount_type == 'percent' and price_include:
                return base_amount - (base_amount / (1 + self.amount / 100))
            if self.amount_type == 'division' and not price_include:
                return base_amount / (1 - self.amount / 100) - base_amount

        if self.amount_type == 'fixed':
            # Use copysign to take into account the sign of the base amount which includes the sign
            # of the quantity and the sign of the price_unit
            # Amount is the fixed price for the tax, it can be negative
            # Base amount included the sign of the quantity and the sign of the unit price and when
            # a product is returned, it can be done either by changing the sign of quantity or by changing the
            # sign of the price unit.
            # When the price unit is equal to 0, the sign of the quantity is absorbed in base_amount then
            # a "else" case is needed.
            if base_amount:
                return math.copysign(quantity, base_amount) * self.amount
            else:
                return quantity * self.amount
        if (self.amount_type == 'percent' and not self.price_include) or (
                self.amount_type == 'division' and self.price_include):
            return base_amount * self.amount / 100
        if self.amount_type == 'percent' and self.price_include:
            return base_amount - (base_amount / (1 + self.amount / 100))
        if self.amount_type == 'division' and not self.price_include:
            return base_amount / (1 - self.amount / 100) - base_amount

        # return super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity, product, partner)



class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name = 'product.template'

    landing_cost = fields.Float(string="Landing Cost")