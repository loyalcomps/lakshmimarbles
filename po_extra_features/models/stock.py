# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _prepare_picking(self):
        picking_vals = super(PurchaseOrder, self)._prepare_picking()
        picking_vals.update({'discount':self.discount,
                             'discount_type':self.discount_type,
                             'discount_amt':self.discount_amt,
                             'round_off_value':self.round_off_value,
                             'round_off_operation':self.round_off_operation,
                             })

        return picking_vals

class StockPicking(models.Model):
    _inherit = "stock.picking"

    discount = fields.Float(string="Discount", digits=dp.get_precision('Discount'), default=0.0)
    discount_type = fields.Selection([('percent', "Percentage"), ('amount', "Amount")], string="Discount type")
    discount_amt = fields.Float(string="Discount", digits=dp.get_precision('Discount'), default=0.0, store=True)
    round_off_value = fields.Float(string="Round Off", default=0.0)
    round_off_operation = fields.Selection([('plus', '+'), ('minus', '-')], string='Round Off Operation')
    rounded_total = fields.Float(compute='_amount_all', string='Rounded Value', default=0.0)

    @api.onchange('discount_type', 'discount', )
    def _onchange_discount(self):
        disc_amount = 0
        if self.discount_type == "amount":
            if self.discount >= self.amount_untaxed + self.amount_tax:
                raise UserError(('Cannot give discount more than total amount.'))
            self.discount_amt = self.discount
        if self.discount_type == "percent":
            disc_amount = ((self.amount_untaxed + self.amount_tax) * self.discount) / 100
            if disc_amount >= self.amount_untaxed + self.amount_tax:
                raise UserError(('Cannot give discount more than total amount.'))
            self.discount_amt = disc_amount


    @api.depends('discount_amt','round_off_value','round_off_operation')
    def _amount_all(self):

        res = super(StockPicking, self)._amount_all()
        for order in self:
            if order.round_off_operation == 'plus' and order.amount_total:
                rounded_total = order.round_off_value
            elif order.round_off_operation == 'minus' and order.amount_total:
                rounded_total = order.round_off_value * -1
            else:
                rounded_total =0

            order.update({
                'rounded_total':order.currency_id.round(rounded_total),
                'amount_discount':order.currency_id.round(order.amount_discount+order.discount_amt) if order.amount_total else 0,
                'amount_total': order.currency_id.round(order.amount_total -order.discount_amt+rounded_total) if order.amount_total else 0,
            })

