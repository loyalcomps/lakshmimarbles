# -*- coding: utf-8 -*-
from odoo import models,fields, api
import time
import logging

_logger = logging.getLogger(__name__)


# class pos_order(models.Model):
#     _inherit = 'pos.order'
#     _name='pos.order'
#
#
#
#     salesperson_name = fields.Char(string='salesperson', size=128),
#
#
#     def _order_fields(self,ui_order):
#         fields = super(pos_order, self)._order_fields()
#         fields['salesperson_name'] = ui_order.get('salesperson_name')
#         return fields
