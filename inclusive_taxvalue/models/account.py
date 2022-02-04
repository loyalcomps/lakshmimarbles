# -*- coding: utf-8 -*-

import math

from odoo import models, fields, api,_
from odoo.tools import float_is_zero
from odoo.exceptions import UserError

import odoo.addons.decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"



    inclusive_value = fields.Boolean('inclusive', default=False, related='invoice_id.inclusive_value')




    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'inclusive_value')
    def _compute_price(self):
        res = super(AccountInvoiceLine, self)._compute_price()
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            if self.invoice_id.inclusive_value:
                taxes = self.invoice_line_tax_ids.with_context(price_include=True,include_base_amount=True).compute_all_inc(price, currency,
                                                                                               self.quantity,
                                                                                               product=self.product_id,
                                                                                               partner=self.invoice_id.partner_id)
            else:
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                              partner=self.invoice_id.partner_id)

        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(
                price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign


    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id','inclusive_value')
    def _compute_price_tax(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        prec = currency.decimal_places
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        q = 1
        unit_taxes = False
        taxes = False
        if self.invoice_line_tax_ids:
            if self.invoice_id.inclusive_value:
                unit_taxes = self.invoice_line_tax_ids.with_context(price_include=True,include_base_amount=True).compute_all_inc(price, currency, q, product=self.product_id,
                                                                   partner=self.invoice_id.partner_id)
                taxes = self.invoice_line_tax_ids.with_context(price_include=True,include_base_amount=True).compute_all_inc(price, currency, self.quantity, product=self.product_id,
                                                           partner=self.invoice_id.partner_id)
            else:
                unit_taxes = self.invoice_line_tax_ids.compute_all(price, currency, q, product=self.product_id,
                                                                   partner=self.invoice_id.partner_id)
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                      partner=self.invoice_id.partner_id)

        self.price_unit_tax = unit_taxes['total_excluded'] if unit_taxes else  price
        self.price_subtotal_tax = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_subtotal_taxinc = taxes['total_included'] if taxes else self.quantity * price
        if self.invoice_id:
            self.price_subtotal_tax = round(self.price_subtotal_tax, prec)
            self.price_subtotal_taxinc = round(self.price_subtotal_taxinc, prec)
            self.price_unit_tax = self.invoice_id.currency_id.round(self.price_unit_tax)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity', 'product_id', 'invoice_id.currency_id',
                 'invoice_id.partner_id', 'invoice_id.company_id', 'invoice_id.discount','invoice_id.discount_type','inclusive_value')
    def calculate_calc_residual(self):

        currency = self.invoice_id and self.invoice_id.currency_id or None
        spl_dis = 0.0
        if self.invoice_id.type in ['in_invoice']:
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            if self.invoice_id.inclusive_value:
                taxes = self.invoice_line_tax_ids.with_context(price_include=True,
                                                                       include_base_amount=True).compute_all_inc(price, currency, self.quantity, product=self.product_id,
                                                              partner=self.invoice_id.partner_id)
            else:
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,partner=self.invoice_id.partner_id)
            included_amount = taxes['total_included']
            if self.invoice_id.discount_type == "percent":
                spl_dis = ((included_amount * self.invoice_id.discount) / 100)
            if self.invoice_id.discount_type == "amount":
                total_amount = 0
                for line in self.invoice_id.invoice_line_ids:
                    price_taxed = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

                    if self.invoice_id.inclusive_value:
                        amt_taxes = line.invoice_line_tax_ids.with_context(price_include=True,
                                                                       include_base_amount=True).compute_all_inc(price_taxed, currency, line.quantity,
                                                                          product=line.product_id,
                                                                          partner=line.invoice_id.partner_id)
                    else:

                        amt_taxes = line.invoice_line_tax_ids.compute_all(price_taxed, currency, line.quantity,
                                                                      product=line.product_id,

                                                                      partner=line.invoice_id.partner_id)
                    total_amount += amt_taxes['total_included']
                if total_amount != 0:
                    spl_dis = (included_amount * self.invoice_id.discount / total_amount) if total_amount !=0 else 0
            self.spcl_disc = spl_dis




class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    inclusive_value = fields.Boolean('inclusive', default=False)

    # @api.onchange('purchase_id')
    # def purchase_order_change(self):
    #     res=super(AccountInvoice, self).purchase_order_change(self)
    #
    #
    #     return res







    # @api.one
    # @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
    #              'discount','type','round_off_value','round_off_operation','freight','inclusive_value')
    # def _compute_amount(self):
    #
    #     res = super(AccountInvoice, self)._compute_amount()
    #     self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
    #     self.amount_tax = sum(line.amount for line in self.tax_line_ids)
    #
    #
    #     if self.type in ['in_invoice', 'in_refund']:
    #
    #         self.amount_total = self.amount_untaxed + self.amount_tax - self.discount_amt+self.freight
    #         for line in self.invoice_line_ids:
    #             self.amount_discount += (line.price_unit * line.quantity * line.discount) / 100
    #         self.amount_discount += self.discount_amt
    #         self.amount_freight = self.freight
    #     else:
    #         self.amount_total = self.amount_untaxed + self.amount_tax
    #     if self.round_off_operation == 'plus':
    #         self.amount_total = self.amount_total+self.round_off_value
    #         self.rounded_total = self.round_off_value
    #     elif self.round_off_operation == 'minus':
    #         self.amount_total = self.amount_total-self.round_off_value
    #         self.rounded_total = self.round_off_value*-1
    #     else:
    #         self.amount_total = self.amount_total
    #
    #     amount_total_company_signed = self.amount_total
    #     amount_untaxed_signed = self.amount_untaxed
    #     if self.currency_id and self.currency_id != self.company_id.currency_id:
    #         currency_id = self.currency_id.with_context(date=self.date_invoice)
    #         amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
    #         amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
    #     sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
    #     self.amount_total_company_signed = amount_total_company_signed * sign
    #     self.amount_total_signed = self.amount_total * sign
    #     self.amount_untaxed_signed = amount_untaxed_signed * sign
    #     self.amount_tax=self.amount_tax




