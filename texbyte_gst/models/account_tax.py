# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, api, fields
import logging
_logger = logging.getLogger(__name__)

''' Account Tax '''
class GST_AccountTax(models.Model):
    _inherit = 'account.tax'

    gst_type = fields.Selection([('gst','GST'),
                                ('ugst','UGST'),
                                ('sgst','SGST'),
                                ('utgst','UTGST'),
                                ('cgst','CGST'),
                                ('igst','IGST'),
                                ('none','Non-GST')],
                                default="none",
                                string="GST Type")

    """ Override compute_all method to calculate proper tax included amount. See odoo PR 16922 in github """
    @api.multi
    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):
        """ Returns all information required to apply taxes (in self + their children in case of a tax goup).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }]
        } """
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
        taxes_to_recompute = {}

        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        prec = currency.decimal_places

        # In some cases, it is necessary to force/prevent the rounding of the tax and the total
        # amounts. For example, in SO/PO line, we don't want to round the price unit at the
        # precision of the currency.
        # The context key 'round' allows to force the standard behavior.
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5

        base_values = self.env.context.get('base_values')
        if not base_values:
            total_excluded = total_included = base = round(price_unit * quantity, prec)
        else:
            total_excluded, total_included, base = base_values

        origin_base = base

        # Sorting key is mandatory in this case. When no key is provided, sorted() will perform a
        # search. However, the search method is overridden in account.tax in order to add a domain
        # depending on the context. This domain might filter out some taxes from self, e.g. in the
        # case of group taxes.
        for tax in self.sorted(key=lambda r: r.sequence):
            if tax.amount_type == 'group':
                children = tax.children_tax_ids.with_context(base_values=(total_excluded, total_included, base))
                ret = children.compute_all(price_unit, currency, quantity, product, partner)
                total_excluded = ret['total_excluded']
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                base = ret['base'] + tax_amount if tax.include_base_amount else ret['base']
                taxes += ret['taxes']
                continue

            tax_amount = tax._compute_amount(base, price_unit, quantity, product, partner)
            tax_amount = self._rounding_preference(tax_amount, round_tax, currency, prec)

            if tax.price_include:
                total_excluded -= tax_amount
                base -= tax_amount
            else:
                total_included += tax_amount

            taxes.append({
                'id': tax.id,
                'name': tax.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': tax_amount,
                'base': base,
                'sequence': tax.sequence,
                'account_id': tax.account_id.id,
                'refund_account_id': tax.refund_account_id.id,
                'analytic': tax.analytic,
            })

            if tax.include_base_amount:
                base += tax_amount

            # Keep track of taxes to recompute
            if tax.price_include and not tax.include_base_amount and tax.amount_type == 'percent':
                taxes_to_recompute[tax.id] = tax.amount

        # If several included taxes not included in the base amount apply, the calculated amount is
        # at the moment incorrect. For example, 126 EUR including a 21 % tax and a 5 % tax.
        if len(taxes_to_recompute) > 1:
            total_excluded = self._filter_taxes_included_base_not_affected(taxes, taxes_to_recompute, origin_base, round_tax, currency, prec)

        return {
            'taxes': sorted(taxes, key=lambda k: k['sequence']),
            'total_excluded': currency.round(total_excluded) if round_total else total_excluded,
            'total_included': currency.round(total_included) if round_total else total_included,
            'base': base,
        }

    """ Recompute the included taxes """
    def _filter_taxes_included_base_not_affected(self, taxes, taxes_to_recompute, origin_base, round_tax, currency, precision):
        taxes_cumul_rate = sum(taxes_to_recompute.values())
        total_excluded = origin_base / (1 + (taxes_cumul_rate / 100)) if taxes_cumul_rate != -100 else 0.0
        for tax in taxes:
            if tax['id'] in taxes_to_recompute:
                tax['base'] = total_excluded
                tax_amount = total_excluded * taxes_to_recompute[tax['id']] / 100
                tax['amount'] = self._rounding_preference(tax_amount, round_tax, currency, precision)
        return total_excluded


    def _rounding_preference(self, tax_amount, bool_round_tax, currency, precision):
        if not bool_round_tax:
            return round(tax_amount, precision)
        else:
            return currency.round(tax_amount)
