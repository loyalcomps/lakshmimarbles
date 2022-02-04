# -*- coding: utf-8 -*-

from odoo import models, fields, api

class inclusive_taxvalue(models.Model):
    _inherit = "purchase.order"


    inclusive_value = fields.Boolean('inclusive', default=False)

    @api.one
    @api.depends('order_line.price_subtotal', 'order_line.discount_amount')
    def _amount_all(self):

        res = super(inclusive_taxvalue, self)._amount_all()
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_discount += line.discount_amount
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    if order.inclusive_value:
                        price = line.price_unit * (1 - ((line.discount_percentage or 0.0) / 100.0))
                        taxes = line.taxes_id.with_context(price_include=True,
                                                           include_base_amount=True).compute_all_inc(price,
                                                                                                     line.order_id.currency_id,
                                                                                                     line.product_qty,
                                                                                                     product=line.product_id,
                                                                                                     partner=line.order_id.partner_id)
                    else:

                        taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, line.product_qty,
                                                          product=line.product_id, partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
                'amount_discount': amount_discount
            })


class PurchaseOrderline(models.Model):
    _inherit = "purchase.order.line"

    @api.one
    @api.depends('discount_amount','order_id.inclusive_value')
    def _compute_amount(self):
        res=super(PurchaseOrderline, self)._compute_amount()
        for line in self:
            price = line.price_unit * (1 - ((line.discount_percentage or 0.0) / 100.0))
            if line.order_id.inclusive_value:
                taxes = self.taxes_id.with_context(price_include=True,
                                                               include_base_amount=True).compute_all_inc(price,
                                                                                                         line.order_id.currency_id,
                                                                                                         line.product_qty,
                                                                                                         product=line.product_id,
                                                                                                         partner=line.order_id.partner_id)
            else:

                taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, line.product_qty,
                                              product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.one
    @api.depends('price_unit', 'discount_percentage', 'taxes_id', 'product_qty',
                 'product_id', 'order_id.partner_id', 'order_id.currency_id', 'order_id.inclusive_value')
    def _compute_price_tax(self):
        currency = self.order_id and self.order_id.currency_id or None
        # prec = currency.decimal_places
        price = self.price_unit * (1 - (self.discount_percentage or 0.0) / 100.0)
        q = 1
        if self.order_id.inclusive_value:
            unit_taxes = self.taxes_id.with_context(price_include=True,
                                                    include_base_amount=True).compute_all_inc(price,
                                                                                              currency, q,
                                                                                              product=self.product_id,
                                                                                              partner=self.order_id.partner_id)
            taxes = self.taxes_id.with_context(price_include=True,
                                               include_base_amount=True).compute_all_inc(price, currency,
                                                                                         self.product_qty,
                                                                                         product=self.product_id,
                                                                                         partner=self.order_id.partner_id)
        else:
            unit_taxes = self.taxes_id.compute_all(price, currency, q, product=self.product_id,
                                                   partner=self.order_id.partner_id)
            taxes = self.taxes_id.compute_all(price, currency, self.product_qty, product=self.product_id,
                                              partner=self.order_id.partner_id)
        self.price_unit_tax = unit_taxes['total_excluded']
        self.price_subtotal_tax = taxes['total_excluded']
        self.price_subtotal_taxinc = taxes['total_included']
        if self.order_id:
            self.price_subtotal_tax = round(self.price_subtotal_tax)
            self.price_subtotal_taxinc = self.price_subtotal_taxinc
            self.price_unit_tax = self.order_id.currency_id.round(self.price_unit_tax)

