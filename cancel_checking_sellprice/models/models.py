# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class cancel_value_sellprice(models.Model):
    _inherit = "purchase.order.line"

    is_check = fields.Boolean('Checking', default=True,related='order_id.is_checking')

    @api.multi
    @api.depends('order_id.is_checking')
    def _checking_status(self):

        for line in self:
            if line.order_id.is_checking == False:
                line.is_check = False
            if line.order_id.is_checking == True:
                line.is_check = True

    # @api.multi
    # @api.depends('is_checking')
    # def _checking_status(self):
    #
    #     for line in self:
    #         if line.is_checking==False:
    #             line.is_check=False
    #         else:
    #             line.is_check=True




class Account_value_sellprice(models.Model):
    _inherit = "account.invoice.line"

    is_check = fields.Boolean('Checking',default=True,related='invoice_id.is_checking')

    @api.multi
    @api.depends('invoice_id.is_checking')
    def _checking_status_value(self):

        for line in self:
            if line.invoice_id.is_checking==False:
                line.is_check=False
            if line.invoice_id.is_checking == True:
                line.is_check=True


    # @api.multi
    # @api.depends('is_checking')
    # def _checking_status_value(self):
    #
    #     for line in self:
    #         if line.is_checking==False:
    #             line.is_check=False
    #         else:
    #             line.is_check=True
    #

