# -*- coding: utf-8 -*-

from odoo import models, fields, api


class barcode_settings(models.Model):
    _name ='item.barcode'

    customer_name = fields.Char(string='Customer Name')

    customer_address = fields.Char(string='Customer Address')

    mrp_type = fields.Char(string='MRP Type')

    fssai = fields.Char(string='FSSAI')

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

    fssai_x1 = fields.Char(string='fssai x1', default='25')
    fssai_y = fields.Char(string='fssai y', default='225')
    fssai_x2 = fields.Char(string='fssai x2', default='95')

    customer_address_x1 = fields.Char(string='Address x1', default='25')
    customer_address_y = fields.Char(string='Address y', default='225')
    customer_address_x2 = fields.Char(string='Address x2', default='95')

    fnt8 = fields.Char(string='fnt8', default='8')
    fnt9 = fields.Char(string='fnt9', default='9')
    fnt10 = fields.Char(string='fnt10', default='10')
    fnt12 = fields.Char(string='fnt12', default='12')

    mrp_fnt  = fields.Char(string='Mrp fnt', default='8')

    item_fnt  = fields.Char(string='Item fnt', default='8')

    expiryx1 = fields.Char(string='expiry x1', default='25')
    expiryx2 = fields.Char(string='expiry x2', default='225')
    expiryy = fields.Char(string='expiry y', default='95')

    bcode_height = fields.Char(string='bcode_height', default='20')
    bcode_width = fields.Char(string='bcode_width', default='142')


class barcode_settingstwo(models.Model):
    _name = 'item.barcodetwo'

    customer_name = fields.Char(string='Customer Name')

    customer_address = fields.Char(string='Customer Address')

    mrp_type = fields.Char(string='MRP Type')

    fssai = fields.Char(string='FSSAI')

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

    fssai_x1 = fields.Char(string='fssai x1', default='25')
    fssai_y = fields.Char(string='fssai y', default='225')
    fssai_x2 = fields.Char(string='fssai y2', default='95')
    fssai_x3 = fields.Char(string='fssai x3', default='325')

    customer_address_x1 = fields.Char(string='Address x1', default='25')
    customer_address_y = fields.Char(string='Address y', default='225')
    customer_address_x2 = fields.Char(string='Address y2', default='95')
    customer_address_x3 = fields.Char(string='Address x3', default='325')

    expiryx1 = fields.Char(string='expiry x1', default='25')
    expiryx2 = fields.Char(string='expiry x2', default='225')
    expiryy = fields.Char(string='expiry y', default='95')
    expiryx3 = fields.Char(string='expiry x3', default='325')

    fnt8 = fields.Char(string='fnt8', default='8')
    fnt9 = fields.Char(string='fnt9', default='9')
    fnt10 = fields.Char(string='fnt10', default='10')
    fnt12 = fields.Char(string='fnt12', default='12')

    mrp_fnt = fields.Char(string='Mrp fnt', default='8')

    item_fnt = fields.Char(string='Item fnt', default='8')

    bcode_height = fields.Char(string='bcode_height', default='20')
    bcode_width = fields.Char(string='bcode_width', default='142')