# -*- coding: utf-8 -*-
from odoo import api, models, fields

class barcode_rule(models.Model):

    _inherit = "barcode.rule"

    type = fields.Selection(selection_add=[
        ('order', 'Order'),

    ])

