# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    margin_discount_perc = fields.Float(string='Margin Discount%',default=0)

    margin_discount = fields.Float(string='Margin Discount',default=0)

    profit = fields.Float(string='Profit',default=0)

    profit_perc = fields.Float(string='Profit%',default=0)


