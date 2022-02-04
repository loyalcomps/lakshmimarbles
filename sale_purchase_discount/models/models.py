# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    if line.discount_amt and not line.discount:
                        price = line.price_unit - (line.discount_amt/line.product_uom_qty) if line.product_uom_qty else line.price_unit
                    else:
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                    product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.multi
    def _get_tax_amount_by_group(self):
        self.ensure_one()
        res = {}
        currency = self.currency_id or self.company_id.currency_id
        for line in self.order_line:
            base_tax = 0
            for tax in line.tax_id:
                group = tax.tax_group_id
                res.setdefault(group, 0.0)
                # FORWARD-PORT UP TO SAAS-17
                if line.discount_amt and not line.discount:
                    price_reduce = line.price_unit - (line.discount_amt/line.product_uom_qty) if line.product_uom_qty else line.price_unit
                else:
                    price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = tax.compute_all(price_reduce + base_tax, quantity=line.product_uom_qty,
                                        product=line.product_id, partner=self.partner_shipping_id)['taxes']
                for t in taxes:
                    res[group] += t['amount']
                if tax.include_base_amount:
                    base_tax += tax.compute_all(price_reduce + base_tax, quantity=1, product=line.product_id,
                                                partner=self.partner_shipping_id)['taxes'][0]['amount']
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        res = map(lambda l: (l[0].name, l[1]), res)
        return res



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_amt = fields.Float(
        string='Discount Amt', digits=dp.get_precision('Discount'),
    )

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','discount_amt')
    def _compute_amount(self):
        for line in self:
            if line.discount_amt and not line.discount:
                price = line.price_unit - (line.discount_amt/line.product_uom_qty) if line.product_uom_qty else line.price_unit
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })


    @api.depends('price_unit', 'discount','discount_amt')
    def _get_price_reduce(self):
        for line in self:
            if line.discount_amt and not line.discount:
                line.price_reduce = line.price_unit - (line.discount_amt/line.product_uom_qty) if line.product_uom_qty else line.price_unit
            else:
                line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0)

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.
        """
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'discount_amt':self.discount_amt
        })

        return res
