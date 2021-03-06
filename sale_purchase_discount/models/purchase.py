# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.tools import frozendict


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """In the case that taxes rounding is set to globally, Odoo requires
        again the line price unit, and currently ORM mixes values, so the only
        way to get a proper value is to overwrite that part, losing
        inheritability.
        """
        orders2recalculate = self.filtered(lambda x: (
            x.company_id.tax_calculation_rounding_method ==
            'round_globally' and any(x.mapped('order_line.discount'))
        ))
        super(PurchaseOrder, self)._amount_all()
        for order in orders2recalculate:
            amount_tax = 0
            for line in order.order_line:
                taxes = line.taxes_id.compute_all(
                    line._get_discounted_price_unit(),
                    line.order_id.currency_id,
                    line.product_qty,
                    product=line.product_id,
                    partner=line.order_id.partner_id,
                )
                amount_tax += sum(
                    t.get('amount', 0.0) for t in taxes.get('taxes', [])
                )
            order.update({
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': order.amount_untaxed + amount_tax,
            })


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('discount','discount_amt')
    def _compute_amount(self):
        """ Inject the product price with proper rounding in the context from
        which account.tax::compute_all() is able to retrieve it. The alternate
        context is patched onto self because it can be a NewId passed in the
        onchange the env of which does not support `with_context`. """
        for line in self:
            orig_context = None
            # This is always executed for allowing other modules to use this
            # with different conditions than discount != 0
            discounted_price_unit = line._get_discounted_price_unit()
            if discounted_price_unit != line.price_unit:
                precision = line.order_id.currency_id.decimal_places
                company = line.company_id or self.env.user.company_id
                if company.tax_calculation_rounding_method == 'round_globally':
                    precision += 5
                orig_context = self.env.context
                price = round(
                    line.product_qty * discounted_price_unit, precision)
                self.env.context = frozendict(
                    self.env.context, base_values=(price, price, price))
            super(PurchaseOrderLine, line)._compute_amount()
            if orig_context is not None:
                self.env.context = orig_context

    discount = fields.Float(
        string='Discount (%)', digits=dp.get_precision('Discount'),
    )
    discount_amt = fields.Float(
        string='Discount Amt', digits=dp.get_precision('Discount'),
    )

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]

    def _get_discounted_price_unit(self):
        """Inheritable method for getting the unit price after applying
        discount(s).

        :rtype: float
        :return: Unit price after discount(s).
        """
        self.ensure_one()
        if self.discount_amt and not self.discount:
            return self.price_unit - (self.discount_amt/self.product_qty) if self.product_qty else self.price_unit
        if self.discount:
            return self.price_unit * (1 - self.discount / 100)
        return self.price_unit

    @api.multi
    def _get_stock_move_price_unit(self):
        """Get correct price with discount replacing current price_unit
        value before calling super and restoring it later for assuring
        maximum inheritability.
        """
        price_unit = False
        price = self._get_discounted_price_unit()
        if price != self.price_unit:
            # Only change value if it's different
            price_unit = self.price_unit
            self.price_unit = price
        price = super(PurchaseOrderLine, self)._get_stock_move_price_unit()
        if price_unit:
            self.price_unit = price_unit
        return price
