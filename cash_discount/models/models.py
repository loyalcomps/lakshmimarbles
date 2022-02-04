# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_discount_cash = fields.Boolean(string='Order Discounts', help='Allow the cashier to give discounts on the whole order.')
    discount_pc_cash = fields.Float(string='Discount Percentage', default=10, help='The default discount Cash')
    discount_product_id_cash = fields.Many2one('product.product', string='Discount Product', domain="[('available_in_pos', '=', True)]", help='The product used to model the discount')
