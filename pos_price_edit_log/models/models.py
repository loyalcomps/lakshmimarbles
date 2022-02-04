# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    actual_price = fields.Float(string='Actual Price', default=0)