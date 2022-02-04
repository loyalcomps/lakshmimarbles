# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError

class Account_vendorsell(models.Model):
    _inherit = 'account.invoice.line'


    sell_price=fields.Float(string="Sell Price")
    # landing_cost = fields.Float(string="Landing Cost", store=True)


    @api.multi
    @api.onchange('product_id')
    def onchange_sell_price(self):
        if self.product_id:
            self.sell_price=self.product_id.lst_price
    # @api.model
    # def create(self,values):
    #     line=super(Account_vendorsell ,self).create(values)
    #     line.product_id.list_price = line.sell_price
    #     return line
    # @api.multi
    # def write(self,vals):
    #     sell = super(Account_vendorsell, self).write(vals)
    #     if 'sell_price' in vals:
    #         self.product_id.list_price = vals['sell_price']
    #     return sell
    @api.multi
    @api.constrains('landing_cost','sell_price')
    def _check_something(self):
        for record in self:
            if record.sell_price < record.landing_cost and record.invoice_id.type =='in_invoice':
                raise ValidationError("Sell price should be greater than Landing cost")













