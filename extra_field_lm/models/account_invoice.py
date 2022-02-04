# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _set_taxes(self):
        res = super(AccountInvoiceLine, self)._set_taxes()
        if self.invoice_id.type in ('in_invoice'):
            self.price_unit = 0

    product_mrp = fields.Float(string="MRP",default=0,digits=dp.get_precision('Product Price'))
    brand_id = fields.Many2one('product.brand', string="Brand")
    hsn = fields.Char(string="HSN")
    barcode = fields.Char(string='Barcode')
    sale_price = fields.Float(string="Sale Price", default=0.0,digits=dp.get_precision('Product Price'))
    customer_tax_id = fields.Many2many('account.tax', string='Customer Taxes', required=True,
                                       domain=[('active', '=', True)])

    @api.model
    def create(self, vals):
        res = {}
        if vals['invoice_id']:

            invoice_id = self.env['account.invoice'].search([('id', '=', vals['invoice_id'])])
            if not invoice_id:
                return super(AccountInvoiceLine, self).create(vals)

            if invoice_id.type != 'in_invoice':
                return super(AccountInvoiceLine, self).create(vals)

        if vals['product_id']:

            product_id = self.env['product.product'].search([('id', '=', vals['product_id'])])
            if 'hsn' in vals:
                res['x_hsn_code'] = vals['hsn']
            if 'invoice_line_tax_ids' in vals:
                res['supplier_taxes_id'] = vals['invoice_line_tax_ids']
            if 'customer_tax_id' in vals:
                res['taxes_id'] = vals['customer_tax_id']
            if 'product_mrp' in vals:
                res['product_mrp'] = vals['product_mrp']
            if 'sale_price' in vals:
                res['lst_price'] = vals['sale_price']

            if 'brand_id' in vals:
                res['brand_id'] = vals['brand_id']

            if 'barcode' in vals:
                res['barcode'] = vals['barcode']

            _logger.info('Updated values to Product %s', product_id.name)
            if not product_id:
                return super(AccountInvoiceLine, self).create(vals)
            else:

                product_id.write(res)

        return super(AccountInvoiceLine, self).create(vals)

    @api.multi
    def write(self, vals):
        res = {}

        if self.invoice_id:

            if self.invoice_id.type != 'in_invoice':
                return super(AccountInvoiceLine, self).write(vals)

        if self.product_id:
            product_id = self.env['product.product'].search([('id', '=', self.product_id.id)])
            if 'hsn' in vals:
                res['x_hsn_code'] = vals['hsn']
            if 'invoice_line_tax_ids' in vals:
                res['supplier_taxes_id'] = vals['invoice_line_tax_ids']
            if 'customer_tax_id' in vals:
                res['taxes_id'] = vals['customer_tax_id']
            if 'product_mrp' in vals:
                res['product_mrp'] = vals['product_mrp']
            if 'sale_price' in vals:
                res['lst_price'] = vals['sale_price']

            if 'brand_id' in vals:
                res['brand_id'] = vals['brand_id']

            if 'barcode' in vals:
                res['barcode'] = vals['barcode']

            _logger.info('Product Name %s', product_id.name)
            if not product_id:
                return super(AccountInvoiceLine, self).write(vals)
            else:

                product_id.write(res)
        return super(AccountInvoiceLine, self).write(vals)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()

        self.hsn = self.product_id.x_hsn_code
        self.customer_tax_id = self.product_id.taxes_id.ids
        self.product_mrp = self.product_id.product_mrp
        self.barcode = self.product_id.barcode
        self.brand_id = self.product_id.brand_id.id
        self.sale_price = self.product_id.lst_price
        return res
