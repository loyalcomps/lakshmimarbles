# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    cess_tax_id = fields.Many2one('account.tax', string='Cess Tax',domain=['|', ('active', '=', False), ('active', '=', True)])

    @api.onchange('product_id')
    def onchange_product_id(self):

        res=super(PurchaseOrderLine, self).onchange_product_id()
        self.cess_tax_id = self.product_id.supplier_cess_id

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    amount_cess = fields.Monetary(string='Cess', store=True, readonly=True, compute='_amount_all')




