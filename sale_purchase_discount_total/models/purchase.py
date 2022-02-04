# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import frozendict


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate = fields.Float('Discount Rate', digits_compute=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all',
                                      digits_compute=dp.get_precision('Account'), track_visibility='always')
    discount_amt = fields.Float(string="Discount", digits=dp.get_precision('Discount'), default=0.0, store=True)

    @api.onchange('discount_type', 'discount_rate')
    def _onchange_discount(self):
        disc_amount = 0
        self.discount_amt = 0
        if (self.amount_untaxed + self.amount_tax) > 0:
            if self.discount_type == "amount":
                if self.discount_rate >= self.amount_untaxed + self.amount_tax:
                    raise UserError(('Cannot give discount more than total amount.'))
                self.discount_amt = self.discount_rate
            if self.discount_type == "percent":
                disc_amount = ((self.amount_untaxed + self.amount_tax) * self.discount_rate) / 100
                if disc_amount >= self.amount_untaxed + self.amount_tax:
                    raise UserError(('Cannot give discount more than total amount.'))
                self.discount_amt = disc_amount

    @api.depends('discount_amt')
    def _amount_all(self):
        super(PurchaseOrder, self)._amount_all()
        for order in self:
            order.update({
                'amount_discount': order.currency_id.round(order.discount_amt) if (order.amount_untaxed + order.amount_tax) > 0 else 0,
                'amount_total': order.amount_total - order.discount_amt if (order.amount_untaxed + order.amount_tax) > 0 else order.amount_total,
            })

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        self.discount_type = self.purchase_id.discount_type
        self.discount_rate = self.purchase_id.discount_rate
        self.discount_amt = self.purchase_id.discount_amt
        return super(AccountInvoice, self).purchase_order_change()