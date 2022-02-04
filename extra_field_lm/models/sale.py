# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_mrp = fields.Float(string="MRP",default=0,digits=dp.get_precision('Product Price'))

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:

            self.product_mrp = self.product_id.product_mrp

        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        res=super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'product_mrp':self.product_mrp
        })
        return res