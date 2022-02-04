# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

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
        if (self.amount_untaxed + self.amount_tax)>0:
            if self.discount_type == "amount":
                if self.discount_rate >= self.amount_untaxed + self.amount_tax:
                    raise UserError(('Cannot give discount more than total amount.'))
                self.discount_amt = self.discount_rate
            if self.discount_type == "percent":
                disc_amount = ((self.amount_untaxed + self.amount_tax) * self.discount_rate) / 100
                if disc_amount >= self.amount_untaxed + self.amount_tax:
                    raise UserError(('Cannot give discount more than total amount.'))
                self.discount_amt = disc_amount
    @api.multi
    def _prepare_invoice(self, ):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate,
            'discount_amt': self.discount_amt
        })
        return invoice_vals

    @api.depends('discount_amt')
    def _amount_all(self):
        res = super(SaleOrder, self)._amount_all()

        for order in self:
            order.update({
                'amount_discount': order.pricelist_id.currency_id.round(order.discount_amt) if (order.amount_untaxed + order.amount_tax) > 0 else 0,
                'amount_total': order.amount_total - order.discount_amt if (order.amount_untaxed + order.amount_tax) > 0 else order.amount_total,
            })
            # res.update({
            #
            #     'amount_discount': order.pricelist_id.currency_id.round(order.discount_amt),
            #     'amount_total': order.amount_total-order.discount_amt,
            # })