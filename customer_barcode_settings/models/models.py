# -*- coding: utf-8 -*-

from odoo import models, fields, api

class customer_barcode_settings(models.Model):
    _name = 'customer.barcode.settings'

    barcode_x = fields.Char(string='Barcode X', default='25')
    barcode_y = fields.Char(string='Barcode Y', default='33')

    name_x = fields.Char(string='Name x', default='10')
    name_y = fields.Char(string='Name Y', default='12')

    phone_x = fields.Char(string='Phone X', default='25')
    phone_y = fields.Char(string='Phone Y', default='70')

    mobile_x = fields.Char(string='Mobile X', default='25')
    mobile_y = fields.Char(string='Mobile Y', default='23')

    fnt8 = fields.Char(string='fnt8', default='8')
    fnt9 = fields.Char(string='fnt9', default='9')
    fnt10 = fields.Char(string='fnt10', default='10')
    fnt12 = fields.Char(string='fnt12', default='12')

    bcode_height = fields.Char(string='Barcode Height', default='20')
    bcode_width = fields.Char(string='Barcode Width', default='142')
