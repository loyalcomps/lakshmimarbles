# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    barcode_scan = fields.Char(string='Product Barcode', help="Here you can provide the barcode for the product")

    @api.onchange('barcode_scan', 'product_id')
    def _onchange_barcode_scan(self):
        product_rec = self.env['product.product']
        product_ids = []
        result = {}
        if self.barcode_scan:
            product = product_rec.search([('barcode', '=', self.barcode_scan)])
            if product:
                product_ids.append(product.id)

            product_tmpl_ids = self.env['product.barcode'].search([('barcode', '=', self.barcode_scan)])

            for product_tmpl in product_tmpl_ids:
                product = product_rec.search([('product_tmpl_id', '=', product_tmpl.product_tmpl_id.id)])
                product_ids.append(product.id)
            # if len(product_ids) == 1:
            #     self.product_id = product_ids[0]
            # else:
            result['domain'] = {'product_id': [('id', 'in', product_ids)]}

            return result
        else:
            products = self.env['product.product'].search([]).ids
            result['domain'] = {'product_id': [('id', 'in', products)]}

            return result
