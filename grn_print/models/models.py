# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_ref = fields.Char('Vendor Reference',
        help="Reference of the sales order or bid sent by the vendor. "
            "It's used to do the matching when you receive the "
            "products as this reference is usually written on the "
            "delivery order sent by your vendor.",related='purchase_id.partner_ref')
    date_invoice = fields.Date(string='Invoice Date',copy=False)
