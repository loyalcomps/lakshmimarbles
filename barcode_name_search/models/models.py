# -*- coding: utf-8 -*-

from odoo import models, fields, api

class multi_product_barcode(models.Model):
    _inherit = 'product.barcode'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.barcode + ' ' + '[' + str(record.product_mrp) + ']'+ ' ' + '[' + str(record.list_price) + ']'
            result.append((record.id, name))
        return result
