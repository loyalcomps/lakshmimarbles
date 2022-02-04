# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_mrp = fields.Float(string="MRP",default=0,digits=dp.get_precision('Product Price'))
    brand_id = fields.Many2one('product.brand', string="Brand")
    hsn = fields.Char(string="HSN")
    barcode = fields.Char(string='Barcode')
    sale_price = fields.Float(string="Sale Price", default=0.0,digits=dp.get_precision('Product Price'))

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()

        self.hsn = self.product_id.x_hsn_code
        self.product_mrp = self.product_id.product_mrp
        self.barcode = self.product_id.barcode
        self.brand_id = self.product_id.brand_id.id
        self.sale_price = self.product_id.lst_price
        return res

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _set_additional_fields(self, invoice):
        if self.purchase_line_id:
            product = self.env['product.product'].search([('id', '=', self.purchase_line_id.product_id.id)])
            for pdct in product:
                data = {
                    'brand_id': self.purchase_line_id.brand_id.id,
                    'sale_price': self.purchase_line_id.sale_price,
                    'hsn': self.purchase_line_id.hsn,
                    'customer_tax_id': pdct.taxes_id.ids,
                    'product_mrp': self.purchase_line_id.product_mrp,
                    'barcode': self.purchase_line_id.barcode,
                    'invoice_line_tax_ids':self.purchase_line_id.taxes_id.ids

                }
                self.update(data)
            # product = self.env['product.product'].search([('id','=',self.purchase_line_id.product_id.id)])
            # for pdct in product:
            #     data = {
            #         'brand_id':pdct.brand_id.id,
            #         'sale_price':pdct.lst_price,
            #         'hsn':pdct.x_hsn_code,
            #         'customer_tax_id': pdct.taxes_id.ids,
            #         'product_mrp':pdct.product_mrp,
            #         'barcode':pdct.barcode
            #
            #     }

        super(AccountInvoiceLine, self)._set_additional_fields(invoice)
