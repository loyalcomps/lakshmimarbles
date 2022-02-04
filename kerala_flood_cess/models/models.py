# -*- coding: utf-8 -*-

from odoo import models, fields, api



class AccountTax(models.Model):
    _inherit = 'account.tax'


    kfc_adjust_amount = fields.Float(required=False, digits=(16, 4))

    kfc_cess_adjust_amount = fields.Float(required=False, digits=(16, 4))

    kfc_adjust = fields.Boolean(string='KFC', default=False)

    kfc = fields.Boolean(string='KFC', default=False)

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        res = super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity, product, partner)
        self.ensure_one()
        if self.amount_type == 'percent' and self.price_include:


            if partner:

                if partner.kfc_plot== True:

                    if self.kfc_cess_adjust_amount != 0.0:
                        if self.kfc_adjust_amount == 0.0 and self.kfc_cess_adjust_amount == 0.0:
                            return base_amount - (base_amount / (1 + self.amount / 100))
                        else:
                            return (base_amount - (
                                    base_amount / (1 + self.kfc_adjust_amount / 100))) / self.kfc_cess_adjust_amount

                    else:
                        if self.kfc_adjust_amount == 0.0:
                            return base_amount - (base_amount / (1 + self.amount / 100))
                        else:
                            return (base_amount - (base_amount / (1 + self.kfc_adjust_amount / 100))) / 2


                else:
                    if self.cess_adjust_amount != 0.0:
                        if self.adjust_amount == 0.0 and self.cess_adjust_amount == 0.0:
                            return base_amount - (base_amount / (1 + self.amount / 100))
                        else:
                            return (base_amount - (base_amount / (1 + self.adjust_amount / 100))) / self.cess_adjust_amount

                    else:
                        if self.adjust_amount == 0.0:
                            return base_amount - (base_amount / (1 + self.amount / 100))
                        else:
                            return (base_amount - (base_amount / (1 + self.adjust_amount / 100))) / 2

        return res

    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):
        # res = super(AccountTax, self)._compute_amount(price_unit, currency, quantity, product, partner)
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
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
        for tax in self.sorted(key=lambda r: r.sequence):
            if tax.amount_type == 'group':

                # if partner is None and tax.kfc==False and tax.kfc_adjust_amount==False:
                #
                #     children = tax.children_tax_ids.with_context(
                #         base_values=(total_excluded, total_included, base))
                #     ret = children.compute_all(price_unit, currency, quantity, product, partner)
                #     total_excluded = ret['total_excluded']
                #     base = ret['base'] if tax.include_base_amount else base
                #     total_included = ret['total_included']
                #     tax_amount = total_included - total_excluded
                #     taxes += ret['taxes']
                if partner:


                    if partner.partner_type == 'B2B' and tax.name != 'GST 28% + Cess 12%':
                        children = tax.children_tax_ids.with_context(base_values=(total_excluded, total_included, base))[:2]
                        ret = children.compute_all(price_unit, currency, quantity, product, partner)
                        total_excluded = ret['total_excluded']
                        base = ret['base'] if tax.include_base_amount else base
                        total_included = ret['total_included']
                        tax_amount = total_included - total_excluded
                        taxes += ret['taxes']

                    elif partner.partner_type == 'B2B' and tax.name == 'GST 28% + Cess 12%':
                        children = tax.children_tax_ids.with_context(base_values=(total_excluded, total_included, base))[:3]
                        ret = children.compute_all(price_unit, currency, quantity, product, partner)
                        total_excluded = ret['total_excluded']
                        base = ret['base'] if tax.include_base_amount else base
                        total_included = ret['total_included']
                        tax_amount = total_included - total_excluded
                        taxes += ret['taxes']
                    elif partner.partner_type == 'IMPORT' and tax.name != 'GST 28% + Cess 12%':
                        children = tax.children_tax_ids.with_context(base_values=(total_excluded, total_included, base))[:2]
                        ret = children.compute_all(price_unit, currency, quantity, product, partner)
                        total_excluded = ret['total_excluded']
                        base = ret['base'] if tax.include_base_amount else base
                        total_included = ret['total_included']
                        tax_amount = total_included - total_excluded
                        taxes += ret['taxes']
                    elif partner.partner_type == 'IMPORT' and tax.name == 'GST 28% + Cess 12%':
                        children = tax.children_tax_ids.with_context(base_values=(total_excluded, total_included, base))[:3]
                        ret = children.compute_all(price_unit, currency, quantity, product, partner)
                        total_excluded = ret['total_excluded']
                        base = ret['base'] if tax.include_base_amount else base
                        total_included = ret['total_included']
                        tax_amount = total_included - total_excluded
                        taxes += ret['taxes']
                    else:
                        if partner.x_gstin == False:
                            children = tax.children_tax_ids.with_context(
                                base_values=(total_excluded, total_included, base))
                            ret = children.compute_all(price_unit, currency, quantity, product, partner)
                            total_excluded = ret['total_excluded']
                            base = ret['base'] if tax.include_base_amount else base
                            total_included = ret['total_included']
                            tax_amount = total_included - total_excluded
                            taxes += ret['taxes']
                        else:
                            children = tax.children_tax_ids.with_context(
                                base_values=(total_excluded, total_included, base))
                            ret = children.compute_all(price_unit, currency, quantity, product, partner)
                            total_excluded = ret['total_excluded']
                            base = ret['base'] if tax.include_base_amount else base
                            total_included = ret['total_included']
                            tax_amount = total_included - total_excluded
                            taxes += ret['taxes']
                else:
                    children = tax.children_tax_ids.with_context(
                        base_values=(total_excluded, total_included, base))
                    ret = children.compute_all(price_unit, currency, quantity, product, partner)
                    total_excluded = ret['total_excluded']
                    base = ret['base'] if tax.include_base_amount else base
                    total_included = ret['total_included']
                    tax_amount = total_included - total_excluded
                    taxes += ret['taxes']

                continue

            tax_amount = tax._compute_amount(base, price_unit, quantity, product, partner)
            if not round_tax:
                tax_amount = round(tax_amount, prec)
            else:
                tax_amount = currency.round(tax_amount)

            if tax.price_include:
                total_excluded -= tax_amount
                base -= tax_amount
            else:
                total_included += tax_amount

            # Keep base amount used for the current tax
            tax_base = base

            if tax.include_base_amount:
                base += tax_amount

            taxes.append({
                'id': tax.id,
                'name': tax.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': tax_amount,
                'base': tax_base,
                'sequence': tax.sequence,
                'account_id': tax.account_id.id,
                'refund_account_id': tax.refund_account_id.id,
                'analytic': tax.analytic,
            })

        return {
            'taxes': sorted(taxes, key=lambda k: k['sequence']),
            'total_excluded': currency.round(total_excluded) if round_total else total_excluded,
            'total_included': currency.round(total_included) if round_total else total_included,
            'base': base,
        }




