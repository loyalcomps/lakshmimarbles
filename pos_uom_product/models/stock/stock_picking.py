# -*- coding: utf-8 -*-
from odoo import fields, api, models

class stock_picking(models.Model):
    _inherit = "stock.picking"

    pos_order_id = fields.Many2one('pos.order', 'POS order')


