# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductBrand(models.Model):
    _name = "product.brand"

    name = fields.Char(string="Brand",required=True)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('product.brand', string="Brand")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand', string="Brand", related='product_variant_ids.brand_id')