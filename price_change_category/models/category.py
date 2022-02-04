# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    sale_price = fields.Float(string='Sale Price', )
    min_sale_amt = fields.Float(string='Affordable Price', )


