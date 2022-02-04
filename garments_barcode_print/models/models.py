# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Garment_barcode(models.Model):
    _name ='garment.barcode.settings'

    product_name_x = fields.Char(string='Product Name x')
    product_name_y = fields.Char(string='Product Name y')
    product_name_fontsize = fields.Float(string='Product Font Size')

    article_number_x = fields.Float(string='Article Number x')
    article_number_y = fields.Float(string='Article Number y')
    barcode_x = fields.Float(string='Barcode x')
    barcode_y = fields.Float(string='Barcode y')
    article_barcode_fontsize = fields.Float(string='Article Barcode Size')

    mrp_x = fields.Float(string='MRP x')
    mrp_y = fields.Float(string='MRP y')
    sale_price_x = fields.Float(string='Sale Price x')
    sale_price_y = fields.Float(string='Sale Price y')
    mrp_saleprice_fontsize = fields.Float(string='MRP Sale Price Size')

