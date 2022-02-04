# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    cess_tax_id = fields.Many2one('account.tax',string='Cess tax',domain=['|', ('active', '=', False), ('active', '=', True)])

    @api.multi
    def _compute_tax_id(self):
        res = super(SaleOrderLine, self)._compute_tax_id()
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter cess by the company
            cess = line.product_id.cess_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)

            line.cess_tax_id = fpos.map_tax(cess, line.product_id, line.order_id.partner_shipping_id) if fpos else cess

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','cess_tax_id')
    def _compute_amount(self):

        res = super(SaleOrderLine, self)._compute_amount()

        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.cess_tax_id:
                taxes = line.tax_id.compute_cess_tax(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id, cess_tax_id = line.cess_tax_id)
            else:
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                    product=line.product_id, partner=line.order_id.partner_shipping_id)
            # #cess calculation
            # currency = line.company_id.currency_id
            # taxes = []
            # prec = currency.decimal_places
            # round_tax = False if line.company_id.tax_calculation_rounding_method == 'round_globally' else True
            # round_total = True
            # if not round_tax:
            #     prec += 5
            #
            # total_excluded = total_included = base = round(price * line.product_uom_qty, prec)
            # if line.tax_id.price_include:
            #     if line.cess_tax_id.amount_type == 'fixed':
            #         taxable_value = (price-line.cess_tax_id.amount)/(1+(line.tax_id.amount/100))
            #         cess_tax_amount = line.cess_tax_id.amount
            #         gst_tax_amount = taxable_value * line.tax_id.amount/100
            #     if line.cess_tax_id.amount_type == 'percent':
            #         taxable_value =price / (1+(line.tax_id.amount/100)+(line.cess_tax_id.amount/100))
            #         cess_tax_amount = taxable_value *line.cess_tax_id.amount/100
            #         gst_tax_amount = taxable_value * line.tax_id.amount / 100
            #     if line.cess_tax_id.amount_type == 'group':
            #         child_fixed_amount = 0
            #         child_percent_amount = 0
            #         for child in line.cess_tax_id.children_tax_ids:
            #             if child.amount_type == 'fixed':
            #                 child_fixed_amount = child.amount
            #             if child.amount_type == 'percent':
            #                 child_percent_amount = child.amount
            #         if line.cess_tax_id.whichever_is_higher==True:
            #
            #             taxable_value_fixed = (price - child_fixed_amount) / (1 + (line.tax_id.amount / 100))
            #             taxable_value_percent = price / (
            #             1 + (line.tax_id.amount / 100) + (child_percent_amount / 100))
            #             tax_percent = taxable_value_percent * child_percent_amount/100
            #             if child_fixed_amount> tax_percent:
            #                 taxable_value = taxable_value_fixed
            #                 cess_tax_amount = child_fixed_amount
            #                 gst_tax_amount = taxable_value * line.tax_id.amount / 100
            #             else:
            #                 taxable_value = taxable_value_percent
            #                 cess_tax_amount = tax_percent
            #                 gst_tax_amount = taxable_value * line.tax_id.amount / 100
            #
            #         else:
            #
            #             taxable_value = (price - child_fixed_amount)/(
            #                     1 + (line.tax_id.amount / 100) + (child_percent_amount / 100))
            #             cess_tax_amount = child_fixed_amount+(taxable_value * child_percent_amount / 100)
            #             gst_tax_amount = taxable_value * line.tax_id.amount / 100
            #
            #
            #
            #
            # else:
            #     taxable_value = price
            #     gst_tax_amount = taxable_value * line.tax_id.amount / 100
            #     if line.cess_tax_id.amount_type == 'fixed':
            #
            #         cess_tax_amount = line.cess_tax_id.amount
            #
            #     if line.cess_tax_id.amount_type == 'percent':
            #         cess_tax_amount = taxable_value * line.cess_tax_id.amount / 100
            #     if line.cess_tax_id.amount_type == 'group':
            #         child_fixed_amount = 0
            #         child_percent_amount = 0
            #         for child in line.cess_tax_id.children_tax_ids:
            #             if child.amount_type == 'fixed':
            #                 child_fixed_amount = child.amount
            #             if child.amount_type == 'percent':
            #                 child_percent_amount = child.amount
            #         if line.cess_tax_id.whichever_is_higher == True:
            #
            #             tax_percent = taxable_value * child_percent_amount / 100
            #             if child_fixed_amount > tax_percent:
            #                 cess_tax_amount = child_fixed_amount
            #             else:
            #                 cess_tax_amount = tax_percent
            #         else:
            #
            #             cess_tax_amount = child_fixed_amount + (taxable_value * child_percent_amount / 100)
            #
            #





            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'] ,
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_cess = fields.Monetary(string='Cess', store=True, readonly=True, compute='_amount_all',
                                      track_visibility='always')



