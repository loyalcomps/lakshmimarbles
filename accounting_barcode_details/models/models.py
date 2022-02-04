# -*- coding: utf-8 -*-

from odoo import models, fields, api

class accounting_barcode_details(models.Model):
    _inherit ='item.barcode'


    customer_care_no = fields.Char(string='Customer Care No',default='25')

    batch_x1 = fields.Char(string='batch_x1', default='25')
    batch_x2 = fields.Char(string='batch_x2', default='225')
    batch_y = fields.Char(string='batch_y', default='33')

    cust_care_x1 = fields.Char(string='cust_care_x1', default='25')
    cust_care_x2 = fields.Char(string='cust_care_x2', default='225')
    cust_care_y = fields.Char(string='cust_care_y', default='33')

    net_weight_x1 = fields.Char(string='net_weight_x1', default='25')
    net_weight_x2 = fields.Char(string='net_weight_x2', default='225')
    net_weight_y = fields.Char(string='net_weight_y', default='33')