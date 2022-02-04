# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp




class product_supplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    landing_cost = fields.Float(string='Landing Cost')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):

        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        for l in line:
            var = {
                'brand_id': l.brand_id,
                'category_id':l.category_id,
                'hsn':l.hsn,
                'discount':l.discount_percentage,
                'discount_amount':l.discount_amount,
                # 'customer_tax_id': l.customer_tax_id,
                # 'product_mrp':l.product_mrp,
                'barcode':l.barcode,
                'date_exp':l.date_exp,
                'sale_price': l.product_id.lst_price,
            }
        res.update(var)
        return res




    # Update landing_cost to supplier info window
    @api.multi
    def action_invoice_open(self):
        super(AccountInvoice, self).action_invoice_open()

        for record in self:
            if record.type == 'in_invoice':

                for line in record.invoice_line_ids:
                    partner = record.partner_id if not record.partner_id.parent_id else record.partner_id.parent_id
                    if partner in line.product_id.seller_ids.mapped('name'):
                        currency = partner.property_purchase_currency_id or record.env.user.company_id.currency_id
                        partner_info = self.env['product.supplierinfo'].search(
                            [('name', '=', partner.id), ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
                        partner_info.landing_cost = line.landing_cost
                        partner_info.min_qty = line.quantity
                        partner_info.price = line.price_unit


            return True











class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # update vendor price if vendor info already in product supplier info
    @api.multi
    def _add_supplier_to_product(self):
        res = super(PurchaseOrder, self)._add_supplier_to_product()
        for line in self.order_line:
            # Do not add a contact as a supplier

            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            if partner in line.product_id.seller_ids.mapped('name'):
                currency = partner.property_purchase_currency_id or self.env.user.company_id.currency_id
                partner = self.env['product.supplierinfo'].search(
                    [('name', '=', partner.id), ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
                partner.price = self.currency_id.compute(line.price_unit, currency)
        return res

    amount_discount = fields.Monetary(string="Discount", store=True, readonly=True, track_visibility='always',
                                      compute="_amount_all")

    @api.one
    @api.depends('order_line.price_subtotal','order_line.discount_amount')
    def _amount_all(self):

        res = super(PurchaseOrder, self)._amount_all()
        self.amount_discount = sum(line.discount_amount for line in self.order_line)


class PurchaseOrderline(models.Model):
    _inherit = "purchase.order.line"

    @api.one
    @api.depends('discount_amount')
    def _compute_amount(self):
        res={}

        for line in self:
            if line.discount_percentage:
                res[line.id] =  line.price_unit
                line.price_unit =line.price_unit * (1 - ((line.discount_percentage or 0.0) / 100.0))

            super(PurchaseOrderline, self)._compute_amount()

            if line.discount_percentage:
                line.price_unit=res[line.id]


    @api.depends('price_unit')
    @api.onchange('discount_amount', 'price_unit', 'product_qty')
    def onchange_discount_amt(self):
        if self.price_unit and self.product_qty != 0:
            self.discount_percentage = (self.discount_amount * 100) / (self.price_unit * self.product_qty)

    @api.depends('price_unit')
    @api.onchange('discount_percentage', 'price_unit', 'product_qty')
    def onchange_discount(self):
        if self.price_unit and self.product_qty != 0:
            self.discount_amount = (self.discount_percentage * self.price_unit * self.product_qty) / 100



    brand_id = fields.Many2one('product.brand', string="Brand", )
    category_id = fields.Many2one('product.category', string="Category")
    hsn = fields.Char(string="HSN/SAC")
    # spcl_disc = fields.Float(string='Special Discount(amt)', compute='calculate_calc_residual', store=True, default=0.0)
    discount_amount = fields.Float(string="Discount(amt)", default=0.0)
    discount_percentage = fields.Float(string="Discount(%)", default=0.0)
    customer_tax_id = fields.Many2many('account.tax', string='Customer Taxes',
                                       domain=['|', ('active', '=', False), ('active', '=', True)])

    sl_no = fields.Integer(compute='_get_line_numbers', string='Sl No.', readonly=False, store=True)
    # landing_cost = fields.Float(string="Landing Cost", compute="get_landing_cost", store=True)
    landing_cost = fields.Float(string="Landing Cost", store=True)
    barcode = fields.Char(string='Barcode')

    price_subtotal_tax = fields.Float(compute='_compute_price_tax', string='Taxable Value',
                                      digits=dp.get_precision('Product Price'), store=True)

    price_subtotal_taxinc = fields.Float(compute='_compute_price_tax', string=' Total',
                                         digits=dp.get_precision('Product Price'), store=True)

    price_unit_tax = fields.Float(compute='_compute_price_tax', string='Unit Price(Exc)',
                                  digits=dp.get_precision('Product Price'), store=True)

    date_exp = fields.Integer(string="Best Before", help="Expiry date", copy=False)


    @api.one
    @api.depends('price_unit', 'discount_percentage', 'taxes_id', 'product_qty',
                 'product_id', 'order_id.partner_id', 'order_id.currency_id')
    def _compute_price_tax(self):
        currency = self.order_id and self.order_id.currency_id or None
        # prec = currency.decimal_places
        price = self.price_unit * (1 - (self.discount_percentage or 0.0) / 100.0)
        q = 1
        unit_taxes = self.taxes_id.compute_all(price, currency, q, product=self.product_id,
                                               partner=self.order_id.partner_id)
        taxes = self.taxes_id.compute_all(price, currency, self.product_qty, product=self.product_id,
                                          partner=self.order_id.partner_id)
        self.price_unit_tax = unit_taxes['total_excluded']
        self.price_subtotal_tax = taxes['total_excluded']
        self.price_subtotal_taxinc = taxes['total_included']
        if self.order_id:
            self.price_subtotal_tax = round(self.price_subtotal_tax)
            self.price_subtotal_taxinc = self.price_subtotal_taxinc
            self.price_unit_tax = self.order_id.currency_id.round(self.price_unit_tax)

    @api.depends('product_id')
    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.order_id.order_line:
                line_rec.sl_no = line_num
                line_num += 1

    @api.model
    def create(self, vals):

        if vals['product_id']:

            product_id = self.env['product.product'].search([('id', '=', vals['product_id'])])
            if 'hsn' in vals:
                product_id.hsn = vals['hsn']
            if 'taxes_id' in vals:
                product_id.supplier_taxes_id = vals['taxes_id']
            if 'customer_tax_id' in vals:
                product_id.taxes_id = vals['customer_tax_id']
            # if 'product_mrp' in vals:
            #     product_id.product_mrp = vals['product_mrp']
            if 'brand_id' in vals:
                product_id.brand_id = vals['brand_id']
            if 'category_id' in vals:
                product_id.categ_id = vals['category_id']
            if 'barcode' in vals:
                product_id.barcode = vals['barcode']
            if 'date_exp' in vals:
                product_id.date_exp = vals['date_exp']
            product_id.available_in_pos = True

        return super(PurchaseOrderline, self).create(vals)

    @api.multi
    def write(self, vals):

        if self.product_id:
            product_id = self.env['product.product'].search([('id', '=', self.product_id.id)])
            if 'hsn' in vals:
                product_id.hsn = vals['hsn']
            if 'taxes_id' in vals:
                product_id.supplier_taxes_id = vals['taxes_id']
            if 'customer_tax_id' in vals:
                product_id.taxes_id = vals['customer_tax_id']
            # if 'product_mrp' in vals:
            #     product_id.product_mrp = vals['product_mrp']
            if 'brand_id' in vals:
                product_id.brand_id = vals['brand_id']
            if 'category_id' in vals:
                product_id.categ_id = vals['category_id']
            if 'barcode' in vals:
                product_id.barcode = vals['barcode']
            if 'date_exp' in vals:
                product_id.date_exp = vals['date_exp']
            product_id.available_in_pos = True

        return super(PurchaseOrderline, self).write(vals)

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderline, self).onchange_product_id()

        self.hsn = self.product_id.hsn
        # self.customer_tax_id = self.product_id.taxes_id
        # self.product_mrp = self.product_id.product_mrp
        self.barcode = self.product_id.barcode
        self.brand_id = self.product_id.brand_id
        self.category_id = self.product_id.categ_id



