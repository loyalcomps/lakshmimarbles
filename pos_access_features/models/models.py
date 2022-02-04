# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    disable_price = fields.Boolean(string='Disable Price', help='Disable Price in POS')
    disable_discount = fields.Boolean(string='Disable discount', help='Disable Discount in POS')