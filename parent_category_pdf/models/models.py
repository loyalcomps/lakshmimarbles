# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, _


_logger = logging.getLogger(__name__)


class Account_categoryLine(models.Model):
    _inherit = "account.invoice"

    stock_locations = fields.Many2one('stock.location', domain= [('usage','=','internal')],
                                      string='Select Branch',store=True,required=True)


class categoryLine(models.Model):
    _inherit = "product.category"

    # base_parent = fields.Many2many('product.category', 'Main Parent',compute='base_parent_fun')
    #
    # @api.multi
    # def base_parent_fun(self):
    #     a = []
    #     return self.ids
    #         # a.append(j)
    #         # return j
