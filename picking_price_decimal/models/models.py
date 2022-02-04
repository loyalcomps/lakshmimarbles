# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'stock.pack.operation'

    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('stock pack Unit Price'))

