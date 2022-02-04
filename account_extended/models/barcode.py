# -*- coding: utf-8 -*-

from odoo import models, fields, api





class barcode_settings(models.Model):
    _name ='item.barcode'

    barcode_x1 = fields.Char(string='barcode_x1', default='25')
    barcode_x2 = fields.Char(string='barcode_x2', default='225')
    barcode_y = fields.Char(string='barcode_y', default='33')

    itemname_x1 = fields.Char(string='itemname_x1', default='10')
    itemname_x2 = fields.Char(string='itemname_x2', default='210')
    itemname_y = fields.Char(string='itemname_y', default='12')

    itemcode_x1 = fields.Char(string='itemcode_x1', default='25')
    itemcode_x2 = fields.Char(string='itemcode_x2', default='225')
    itemcode_y = fields.Char(string='itemcode_y', default='70')

    mrp_x1 = fields.Char(string='mrp_x1', default='25')
    mrp_x2 = fields.Char(string='mrp_x2', default='225')
    mrp_y = fields.Char(string='mrp_y', default='23')

    sellprice_x1 = fields.Char(string='sellprice_x1', default='75')
    sellprice_x2 = fields.Char(string='sellprice_x2', default='275')
    sellprice_y = fields.Char(string='sellprice_y', default='70')

    customer_x1 = fields.Char(string='customer_x1', default='40')
    customer_x2 = fields.Char(string='customer_x2', default='240')
    customer_y = fields.Char(string='customer_y', default='0')

    barcount = fields.Char(string='barcount', default='2')
    mrpstatus = fields.Char(string='mrpstatus', default='0')
    datestatus = fields.Char(string='datestatus', default='0')

    datex1 = fields.Char(string='datex1', default='25')
    datex2 = fields.Char(string='datex2', default='225')
    datey = fields.Char(string='datey', default='85')

    dateexpx1 = fields.Char(string='dateexpx1', default='25')
    dateexpy = fields.Char(string='dateexpy', default='225')
    dateexpx2 = fields.Char(string='dateexpx2', default='95')

    fnt8 = fields.Char(string='fnt8', default='8')
    fnt9 = fields.Char(string='fnt9', default='9')
    fnt10 = fields.Char(string='fnt10', default='10')
    fnt12 = fields.Char(string='fnt12', default='12')

    bcode_height = fields.Char(string='bcode_height', default='20')
    bcode_width = fields.Char(string='bcode_width', default='142')


class barcode_settingstwo(models.Model):
    _name = 'item.barcodetwo'

    barcode_x1 = fields.Char(string='barcode_x1', default='25')
    barcode_x2 = fields.Char(string='barcode_x2', default='225')
    barcode_x3 = fields.Char(string='barcode_x3', default='325')
    barcode_y = fields.Char(string='barcode_y', default='33')

    itemname_x1 = fields.Char(string='itemname_x1', default='10')
    itemname_x2 = fields.Char(string='itemname_x2', default='210')
    itemname_x3 = fields.Char(string='itemname_x3', default='310')
    itemname_y = fields.Char(string='itemname_y', default='12')

    itemcode_x1 = fields.Char(string='itemcode_x1', default='25')
    itemcode_x2 = fields.Char(string='itemcode_x2', default='225')
    itemcode_x3 = fields.Char(string='itemcode_x3', default='325')

    itemcode_y = fields.Char(string='itemcode_y', default='70')

    mrp_x1 = fields.Char(string='mrp_x1', default='25')
    mrp_x2 = fields.Char(string='mrp_x2', default='225')
    mrp_x3 = fields.Char(string='mrp_x3', default='325')
    mrp_y = fields.Char(string='mrp_y', default='23')

    sellprice_x1 = fields.Char(string='sellprice_x1', default='75')
    sellprice_x2 = fields.Char(string='sellprice_x2', default='275')
    sellprice_x3 = fields.Char(string='sellprice_x3', default='375')
    sellprice_y = fields.Char(string='sellprice_y', default='70')

    customer_x1 = fields.Char(string='customer_x1', default='40')
    customer_x2 = fields.Char(string='customer_x2', default='240')
    customer_x3 = fields.Char(string='customer_x3', default='340')
    customer_y = fields.Char(string='customer_y', default='0')

    barcount = fields.Char(string='barcount', default='2')
    mrpstatus = fields.Char(string='mrpstatus', default='0')
    datestatus = fields.Char(string='datestatus', default='0')

    datex1 = fields.Char(string='datex1', default='25')
    datex2 = fields.Char(string='datex2', default='225')
    datex3 = fields.Char(string='datex3', default='325')
    datey = fields.Char(string='datey', default='85')

    dateexpx1 = fields.Char(string='dateexpx1', default='25')
    dateexpx2 = fields.Char(string='dateexpx2', default='225')
    dateexpx3 = fields.Char(string='dateexpx3', default='325')
    dateexpy = fields.Char(string='dateexpy', default='95')

    fnt8 = fields.Char(string='fnt8', default='8')
    fnt9 = fields.Char(string='fnt9', default='9')
    fnt10 = fields.Char(string='fnt10', default='10')
    fnt12 = fields.Char(string='fnt12', default='12')

    bcode_height = fields.Char(string='bcode_height', default='20')
    bcode_width = fields.Char(string='bcode_width', default='142')