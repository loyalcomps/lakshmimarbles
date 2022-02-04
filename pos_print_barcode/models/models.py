# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = "pos.config"

    barcode_receipt = fields.Boolean('Barcode receipt', default=0)

class PosOrder(models.Model):
    _inherit = "pos.order"

    ean13_barcode = fields.Char('Barcode')

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get('ean13_barcode', False):
            order_fields.update({
                'ean13_barcode': ui_order['ean13_barcode']
            })
        return order_fields