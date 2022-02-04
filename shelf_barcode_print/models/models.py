# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ShelfBarcodeSettings(models.Model):
    _name ='shelf.barcode.settings'

    article_x = fields.Float(string='Article x')
    article_y = fields.Float(string='Article y')
    iea_x = fields.Float(string='IEA x')
    iea_y = fields.Float(string='IEA y')
    item_x = fields.Float(string='Item x')
    item_y = fields.Float(string='Item y')
    barcode_x = fields.Float(string='Barcode x')
    barcode_y = fields.Float(string='Barcode y')
    price_x = fields.Float(string='Price x')
    price_y = fields.Float(string='Price y')
    date_x = fields.Float(string='Date x')
    date_y = fields.Float(string='Date y')
    uom_x = fields.Float(string='UOM x')
    uom_y = fields.Float(string='UOM y')
    qty_x = fields.Float(string='Qty x')
    qty_y = fields.Float(string='Qty y')

