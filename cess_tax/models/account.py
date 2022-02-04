# -*- coding: utf-8 -*-

import math
from odoo import models, fields, api

class AccountTax(models.Model):
    _inherit = "account.tax"

    cess_per_thousand = fields.Float(string='Cess per Thousand/Tonne')
    whichever_is_higher = fields.Boolean(string='Whichever is Higher')
    cess = fields.Boolean(string='Cess')

    @api.onchange('cess_per_thousand')
    def calculate_amt(self):
        self.amount = self.cess_per_thousand/1000


    @api.multi
    def compute_cess_tax(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, cess_tax_id=None):

        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
        prec = currency.decimal_places
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if not round_tax:
            prec += 5

        total_excluded = total_included = base = round(price_unit * quantity, prec)
        base_value = round(price_unit * quantity, prec)

        for line in self:


            if line.price_include:
                if cess_tax_id.amount_type == 'fixed':
                    taxable_value = (base_value - (cess_tax_id.amount*quantity)) / (1 + (line.amount / 100))
                    cess_tax_amount = cess_tax_id.amount*quantity
                    gst_tax_amount = taxable_value * line.amount / 100
                    if not round_tax:
                        cess_tax_amount = round(cess_tax_amount, prec)
                        gst_tax_amount = round(gst_tax_amount, prec)
                    else:
                        cess_tax_amount = currency.round(cess_tax_amount)
                        gst_tax_amount = currency.round(gst_tax_amount)
                if cess_tax_id.amount_type == 'percent':
                    taxable_value = base_value / (1 + (line.amount / 100) + (cess_tax_id.amount / 100))
                    cess_tax_amount = taxable_value * cess_tax_id.amount / 100
                    gst_tax_amount = taxable_value * line.amount / 100
                    if not round_tax:
                        cess_tax_amount = round(cess_tax_amount, prec)
                        gst_tax_amount = round(gst_tax_amount, prec)
                    else:
                        cess_tax_amount = currency.round(cess_tax_amount)
                        gst_tax_amount = currency.round(gst_tax_amount)
                if cess_tax_id.amount_type == 'group':
                    child_fixed_amount = 0
                    child_percent_amount = 0
                    for child in cess_tax_id.children_tax_ids:
                        if child.amount_type == 'fixed':
                            child_fixed_amount = child.amount*quantity
                        if child.amount_type == 'percent':
                            child_percent_amount = child.amount
                    if cess_tax_id.whichever_is_higher == True:

                        taxable_value_fixed = (base_value - child_fixed_amount) / (1 + (line.amount / 100))
                        taxable_value_percent = base_value / (
                            1 + (line.amount / 100) + (child_percent_amount / 100))
                        tax_percent = taxable_value_percent * child_percent_amount / 100
                        if child_fixed_amount > tax_percent:
                            taxable_value = taxable_value_fixed
                            cess_tax_amount = child_fixed_amount
                            gst_tax_amount = taxable_value * line.amount / 100
                            if not round_tax:
                                cess_tax_amount = round(cess_tax_amount, prec)
                                gst_tax_amount = round(gst_tax_amount, prec)
                            else:
                                cess_tax_amount = currency.round(cess_tax_amount)
                                gst_tax_amount = currency.round(gst_tax_amount)
                            for child_tax in cess_tax_id.children_tax_ids:
                                if child_tax.amount_type == 'fixed':
                                    taxes.append({
                                        'id': child_tax.id,
                                        'name': child_tax.name,
                                        'amount': cess_tax_amount,
                                        'cess': True,
                                        'base': taxable_value,
                                        'sequence': child_tax.sequence,
                                        'account_id': child_tax.account_id.id,
                                        'refund_account_id': child_tax.refund_account_id.id,
                                        'analytic': child_tax.analytic,
                                        })
                        else:
                            taxable_value = taxable_value_percent
                            cess_tax_amount = tax_percent
                            gst_tax_amount = taxable_value * line.amount / 100
                            if not round_tax:
                                cess_tax_amount = round(cess_tax_amount, prec)
                                gst_tax_amount = round(gst_tax_amount, prec)
                            else:
                                cess_tax_amount = currency.round(cess_tax_amount)
                                gst_tax_amount = currency.round(gst_tax_amount)
                            for child_tax in cess_tax_id.children_tax_ids:
                                if child_tax.amount_type == 'percent':
                                    taxes.append({
                                        'id': child_tax.id,
                                        'name': child_tax.name,
                                        'amount': cess_tax_amount,
                                        'cess': True,
                                        'base': taxable_value,
                                        'sequence': child_tax.sequence,
                                        'account_id': child_tax.account_id.id,
                                        'refund_account_id': child_tax.refund_account_id.id,
                                        'analytic': child_tax.analytic,
                                        })

                    else:

                        taxable_value = (base_value - child_fixed_amount) / (
                            1 + (line.amount / 100) + (child_percent_amount / 100))
                        cess_tax_amount = child_fixed_amount + (taxable_value * child_percent_amount / 100)

                        gst_tax_amount = taxable_value * line.amount / 100
                        if not round_tax:
                            cess_tax_amount = round(cess_tax_amount, prec)
                            gst_tax_amount = round(gst_tax_amount, prec)
                        else:
                            cess_tax_amount = currency.round(cess_tax_amount)
                            gst_tax_amount = currency.round(gst_tax_amount)
                        for child_tax in cess_tax_id.children_tax_ids:
                            if child_tax.amount_type == 'percent':
                                taxes.append({
                                    'id': child_tax.id,
                                    'name': child_tax.name,
                                    'amount': cess_tax_amount-child_fixed_amount,
                                    'cess': True,
                                    'base': taxable_value,
                                    'sequence': child_tax.sequence,
                                    'account_id': child_tax.account_id.id,
                                    'refund_account_id': child_tax.refund_account_id.id,
                                    'analytic': child_tax.analytic,
                                })
                            if child_tax.amount_type == 'fixed':
                                taxes.append({
                                    'id': child_tax.id,
                                    'name': child_tax.name,
                                    'amount': child_tax.amount,
                                    'cess': True,
                                    'base': taxable_value,
                                    'sequence': child_tax.sequence,
                                    'account_id': child_tax.account_id.id,
                                    'refund_account_id': child_tax.refund_account_id.id,
                                    'analytic': child_tax.analytic,
                                })

                taxes.append({
                    'id': line.id,
                    'name': line.with_context(**{'lang': partner.lang} if partner else {}).name,
                    'amount': gst_tax_amount,
                    'base': taxable_value,
                    'sequence': line.sequence,
                    'account_id': line.account_id.id,
                    'refund_account_id': line.refund_account_id.id,
                    'analytic': line.analytic,
                })
                if cess_tax_id.amount_type != 'group':
                    taxes.append({
                        'id': cess_tax_id.id,
                        'name': cess_tax_id.name,
                        'amount': cess_tax_amount,
                        'cess': True,
                        'base': taxable_value,
                        'sequence': cess_tax_id.sequence,
                        'account_id': cess_tax_id.account_id.id,
                        'refund_account_id': cess_tax_id.refund_account_id.id,
                        'analytic': cess_tax_id.analytic,
                    })




            else:
                taxable_value = base_value
                gst_tax_amount = taxable_value * line.amount / 100
                if not round_tax:

                    gst_tax_amount = round(gst_tax_amount, prec)
                else:

                    gst_tax_amount = currency.round(gst_tax_amount)
                if cess_tax_id.amount_type == 'fixed':
                    cess_tax_amount = cess_tax_id.amount*quantity
                    if not round_tax:
                        cess_tax_amount = round(cess_tax_amount, prec)
                    else:
                        cess_tax_amount = currency.round(cess_tax_amount)

                if cess_tax_id.amount_type == 'percent':
                    cess_tax_amount = taxable_value * cess_tax_id.amount / 100
                    if not round_tax:
                        cess_tax_amount = round(cess_tax_amount, prec)
                    else:
                        cess_tax_amount = currency.round(cess_tax_amount)
                if cess_tax_id.amount_type == 'group':
                    child_fixed_amount = 0
                    child_percent_amount = 0
                    for child in cess_tax_id.children_tax_ids:
                        if child.amount_type == 'fixed':
                            child_fixed_amount = child.amount*quantity
                        if child.amount_type == 'percent':
                            child_percent_amount = child.amount
                    if cess_tax_id.whichever_is_higher == True:

                        tax_percent = taxable_value * child_percent_amount / 100
                        if child_fixed_amount > tax_percent:
                            cess_tax_amount = child_fixed_amount
                            if not round_tax:
                                cess_tax_amount = round(cess_tax_amount, prec)
                            else:
                                cess_tax_amount = currency.round(cess_tax_amount)
                            for child_tax in cess_tax_id.children_tax_ids:
                                if child_tax.amount_type == 'fixed':
                                    taxes.append({
                                        'id': child_tax.id,
                                        'name': child_tax.name,
                                        'amount': cess_tax_amount,
                                        'cess': True,
                                        'base': taxable_value,
                                        'sequence': child_tax.sequence,
                                        'account_id': child_tax.account_id.id,
                                        'refund_account_id': child_tax.refund_account_id.id,
                                        'analytic': child_tax.analytic,
                                        })
                        else:
                            cess_tax_amount = tax_percent
                            if not round_tax:
                                cess_tax_amount = round(cess_tax_amount, prec)
                            else:
                                cess_tax_amount = currency.round(cess_tax_amount)
                            for child_tax in cess_tax_id.children_tax_ids:
                                if child_tax.amount_type == 'percent':
                                    taxes.append({
                                        'id': child_tax.id,
                                        'name': child_tax.name,
                                        'amount': cess_tax_amount,
                                        'cess': True,
                                        'base': taxable_value,
                                        'sequence': child_tax.sequence,
                                        'account_id': child_tax.account_id.id,
                                        'refund_account_id': child_tax.refund_account_id.id,
                                        'analytic': child_tax.analytic,
                                        })
                    else:

                        cess_tax_amount = child_fixed_amount + (taxable_value * child_percent_amount / 100)
                        if not round_tax:
                            cess_tax_amount = round(cess_tax_amount, prec)
                        else:
                            cess_tax_amount = currency.round(cess_tax_amount)
                        for child_tax in cess_tax_id.children_tax_ids:
                            if child_tax.amount_type == 'percent':
                                taxes.append({
                                    'id': child_tax.id,
                                    'name': child_tax.name,
                                    'amount': cess_tax_amount-child_fixed_amount,
                                    'cess': True,
                                    'base': taxable_value,
                                    'sequence': child_tax.sequence,
                                    'account_id': child_tax.account_id.id,
                                    'refund_account_id': child_tax.refund_account_id.id,
                                    'analytic': child_tax.analytic,
                                })
                            if child_tax.amount_type == 'fixed':
                                taxes.append({
                                    'id': child_tax.id,
                                    'name': child_tax.name,
                                    'amount': child_tax.amount,
                                    'cess': True,
                                    'base': taxable_value,
                                    'sequence': child_tax.sequence,
                                    'account_id': child_tax.account_id.id,
                                    'refund_account_id': child_tax.refund_account_id.id,
                                    'analytic': child_tax.analytic,
                                })

                taxes.append({
                    'id': line.id,
                    'name': line.with_context(**{'lang': partner.lang} if partner else {}).name,
                    'amount': gst_tax_amount,
                    'base': taxable_value,
                    'sequence': line.sequence,
                    'account_id': line.account_id.id,
                    'refund_account_id': line.refund_account_id.id,
                    'analytic': line.analytic,
                })
                if cess_tax_id.amount_type != 'group':
                    taxes.append({
                        'id': cess_tax_id.id,
                        'name': cess_tax_id.name,
                        'amount': cess_tax_amount,
                        'cess':True,
                        'base': taxable_value,
                        'sequence': cess_tax_id.sequence,
                        'account_id': cess_tax_id.account_id.id,
                        'refund_account_id': cess_tax_id.refund_account_id.id,
                        'analytic': cess_tax_id.analytic,
                    })
            if line.price_include:
                total_excluded -= (gst_tax_amount+cess_tax_amount)
                base -= (gst_tax_amount+cess_tax_amount)
            else:
                total_included += (gst_tax_amount+cess_tax_amount)

        return {
            'taxes': sorted(taxes, key=lambda k: k['sequence']),
            'total_excluded': currency.round(total_excluded) if round_total else total_excluded,
            'total_included': currency.round(total_included) if round_total else total_included,
            'base': base,
        }

    @api.multi
    def compute_cess_tax_include(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, cess_tax_id=None):

        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
        prec = currency.decimal_places
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if not round_tax:
            prec += 5

        total_excluded = total_included = base = round(price_unit * quantity, prec)
        base_value = round(price_unit * quantity, prec)

        for line in self:


            if cess_tax_id.amount_type == 'fixed':
                taxable_value = (base_value - (cess_tax_id.amount * quantity)) / (1 + (line.amount / 100))
                cess_tax_amount = cess_tax_id.amount * quantity
                gst_tax_amount = taxable_value * line.amount / 100
                if not round_tax:
                    cess_tax_amount = round(cess_tax_amount, prec)
                    gst_tax_amount = round(gst_tax_amount, prec)
                else:
                    cess_tax_amount = currency.round(cess_tax_amount)
                    gst_tax_amount = currency.round(gst_tax_amount)
            if cess_tax_id.amount_type == 'percent':
                taxable_value = base_value / (1 + (line.amount / 100) + (cess_tax_id.amount / 100))
                cess_tax_amount = taxable_value * cess_tax_id.amount / 100
                gst_tax_amount = taxable_value * line.amount / 100
                if not round_tax:
                    cess_tax_amount = round(cess_tax_amount, prec)
                    gst_tax_amount = round(gst_tax_amount, prec)
                else:
                    cess_tax_amount = currency.round(cess_tax_amount)
                    gst_tax_amount = currency.round(gst_tax_amount)
            if cess_tax_id.amount_type == 'group':
                child_fixed_amount = 0
                child_percent_amount = 0
                for child in cess_tax_id.children_tax_ids:
                    if child.amount_type == 'fixed':
                        child_fixed_amount = child.amount * quantity
                    if child.amount_type == 'percent':
                        child_percent_amount = child.amount
                if cess_tax_id.whichever_is_higher == True:

                    taxable_value_fixed = (base_value - child_fixed_amount) / (1 + (line.amount / 100))
                    taxable_value_percent = base_value / (
                            1 + (line.amount / 100) + (child_percent_amount / 100))
                    tax_percent = taxable_value_percent * child_percent_amount / 100
                    if child_fixed_amount > tax_percent:
                        taxable_value = taxable_value_fixed
                        cess_tax_amount = child_fixed_amount
                        gst_tax_amount = taxable_value * line.amount / 100
                        if not round_tax:
                            cess_tax_amount = round(cess_tax_amount, prec)
                            gst_tax_amount = round(gst_tax_amount, prec)
                        else:
                            cess_tax_amount = currency.round(cess_tax_amount)
                            gst_tax_amount = currency.round(gst_tax_amount)
                        for child_tax in cess_tax_id.children_tax_ids:
                            if child_tax.amount_type == 'fixed':
                                taxes.append({
                                    'id': child_tax.id,
                                    'name': child_tax.name,
                                    'amount': cess_tax_amount,
                                    'cess': True,
                                    'base': taxable_value,
                                    'sequence': child_tax.sequence,
                                    'account_id': child_tax.account_id.id,
                                    'refund_account_id': child_tax.refund_account_id.id,
                                    'analytic': child_tax.analytic,
                                })
                    else:
                        taxable_value = taxable_value_percent
                        cess_tax_amount = tax_percent
                        gst_tax_amount = taxable_value * line.amount / 100
                        if not round_tax:
                            cess_tax_amount = round(cess_tax_amount, prec)
                            gst_tax_amount = round(gst_tax_amount, prec)
                        else:
                            cess_tax_amount = currency.round(cess_tax_amount)
                            gst_tax_amount = currency.round(gst_tax_amount)
                        for child_tax in cess_tax_id.children_tax_ids:
                            if child_tax.amount_type == 'percent':
                                taxes.append({
                                    'id': child_tax.id,
                                    'name': child_tax.name,
                                    'amount': cess_tax_amount,
                                    'cess': True,
                                    'base': taxable_value,
                                    'sequence': child_tax.sequence,
                                    'account_id': child_tax.account_id.id,
                                    'refund_account_id': child_tax.refund_account_id.id,
                                    'analytic': child_tax.analytic,
                                })

                else:

                    taxable_value = (base_value - child_fixed_amount) / (
                        1 + (line.amount / 100) + (child_percent_amount / 100))
                    cess_tax_amount = child_fixed_amount + (taxable_value * child_percent_amount / 100)

                    gst_tax_amount = taxable_value * line.amount / 100
                    if not round_tax:
                        cess_tax_amount = round(cess_tax_amount, prec)
                        gst_tax_amount = round(gst_tax_amount, prec)
                    else:
                        cess_tax_amount = currency.round(cess_tax_amount)
                        gst_tax_amount = currency.round(gst_tax_amount)
                    for child_tax in cess_tax_id.children_tax_ids:
                        if child_tax.amount_type == 'percent':
                            taxes.append({
                                'id': child_tax.id,
                                'name': child_tax.name,
                                'amount': cess_tax_amount - child_fixed_amount,
                                'cess': True,
                                'base': taxable_value,
                                'sequence': child_tax.sequence,
                                'account_id': child_tax.account_id.id,
                                'refund_account_id': child_tax.refund_account_id.id,
                                'analytic': child_tax.analytic,
                            })
                        if child_tax.amount_type == 'fixed':
                            taxes.append({
                                'id': child_tax.id,
                                'name': child_tax.name,
                                'amount': child_tax.amount,
                                'cess': True,
                                'base': taxable_value,
                                'sequence': child_tax.sequence,
                                'account_id': child_tax.account_id.id,
                                'refund_account_id': child_tax.refund_account_id.id,
                                'analytic': child_tax.analytic,
                            })

            taxes.append({
                'id': line.id,
                'name': line.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': gst_tax_amount,
                'base': taxable_value,
                'sequence': line.sequence,
                'account_id': line.account_id.id,
                'refund_account_id': line.refund_account_id.id,
                'analytic': line.analytic,
            })
            if cess_tax_id.amount_type != 'group':
                taxes.append({
                    'id': cess_tax_id.id,
                    'name': cess_tax_id.name,
                    'amount': cess_tax_amount,
                    'cess': True,
                    'base': taxable_value,
                    'sequence': cess_tax_id.sequence,
                    'account_id': cess_tax_id.account_id.id,
                    'refund_account_id': cess_tax_id.refund_account_id.id,
                    'analytic': cess_tax_id.analytic,
                })





            total_excluded -= (gst_tax_amount + cess_tax_amount)
            base -= (gst_tax_amount + cess_tax_amount)


        return {
            'taxes': sorted(taxes, key=lambda k: k['sequence']),
            'total_excluded': currency.round(total_excluded) if round_total else total_excluded,
            'total_included': currency.round(total_included) if round_total else total_included,
            'base': base,
        }

    def _compute_amount_include(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        self.ensure_one()
        if self.amount_type == 'fixed':
            # Use copysign to take into account the sign of the base amount which includes the sign
            # of the quantity and the sign of the price_unit
            # Amount is the fixed price for the tax, it can be negative
            # Base amount included the sign of the quantity and the sign of the unit price and when
            # a product is returned, it can be done either by changing the sign of quantity or by changing the
            # sign of the price unit.
            # When the price unit is equal to 0, the sign of the quantity is absorbed in base_amount then
            # a "else" case is needed.
            if base_amount:
                return math.copysign(quantity, base_amount) * self.amount
            else:
                return quantity * self.amount

        if self.amount_type == 'percent' :
            return base_amount - (base_amount / (1 + self.amount / 100))
        if self.amount_type == 'division' :
            return base_amount / (1 - self.amount / 100) - base_amount
    @api.multi
    def compute_all_include(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):

        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
        prec = currency.decimal_places
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if not round_tax:
            prec += 5

        base_values = self.env.context.get('base_values')
        if not base_values:
            total_excluded = total_included = base = round(price_unit * quantity, prec)
        else:
            total_excluded, total_included, base = base_values

        for tax in self.sorted(key=lambda r: r.sequence):
            if tax.amount_type == 'group':
                children = tax.children_tax_ids.with_context(base_values=(total_excluded, total_included, base))
                ret = children.compute_all_include(price_unit, currency, quantity, product, partner)
                total_excluded = ret['total_excluded']
                base = ret['base'] if tax.include_base_amount else base
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue

            tax_amount = tax._compute_amount_include(base, price_unit, quantity, product, partner)
            if not round_tax:
                tax_amount = round(tax_amount, prec)
            else:
                tax_amount = currency.round(tax_amount)

            total_excluded -= tax_amount
            base -= tax_amount

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
class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    cess_tax_id = fields.Many2one('account.tax', string='Cess Tax',
                                            domain=[('type_tax_use', '!=', 'none'), '|', ('active', '=', False),
                                                    ('active', '=', True)])
    cess_amount = fields.Monetary(string='Amount',
                                     store=True, readonly=True, compute='_compute_price')
    visible_cess = fields.Boolean(related='invoice_id.visible_cess')
    def _set_taxes(self):
        res=super(AccountInvoiceLine, self)._set_taxes()
        """ Used in on_change to set taxes and price."""
        if self.invoice_id.type in ('out_invoice', 'out_refund'):
            cess_taxes = self.product_id.cess_id
        else:
            cess_taxes = self.product_id.supplier_cess_id
        # Keep only taxes of the company
        company_id = self.company_id or self.env.user.company_id
        cess_taxes = cess_taxes.filtered(lambda r: r.company_id == company_id)

        self.cess_tax_id = self.invoice_id.fiscal_position_id.map_tax(cess_taxes, self.product_id,
                                                                                          self.invoice_id.partner_id)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice','cess_tax_id','invoice_id.include','scheme_discount_amount','scheme_discount')
    def _compute_price(self):
        res=super(AccountInvoiceLine, self)._compute_price()
        currency = self.invoice_id and self.invoice_id.currency_id or None
        if self.invoice_id.type == 'in_invoice':
            base_price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            disc_amt = self.scheme_discount_amount/self.quantity

            disc_per = (base_price * self.scheme_discount) / 100
            price = base_price - disc_per-disc_amt
        else:
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_id.type in ['in_invoice', 'in_refund'] and self.invoice_id.include == True:
            if self.cess_tax_id:
                taxes = self.invoice_line_tax_ids.compute_cess_tax_include(price, currency, self.quantity,
                                                                           product=self.product_id,
                                                                           partner=self.invoice_id.partner_id,
                                                                           cess_tax_id=self.cess_tax_id)
            else:
                taxes = self.invoice_line_tax_ids.compute_all_include(price,currency, self.quantity,
                                                                      product=self.product_id,
                                                                      partner=self.invoice_id.partner_id)

        else:


            if self.cess_tax_id:
                taxes = self.invoice_line_tax_ids.compute_cess_tax(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id,  cess_tax_id = self.cess_tax_id)
            else:
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                              partner=self.invoice_id.partner_id)

        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if taxes:
            for tax in taxes['taxes']:
                if 'cess' in tax and tax['cess']== True:
                    self.cess_amount = tax['amount']
                else:
                    self.cess_amount = 0.0
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(
                price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    amount_cess = fields.Monetary(string='Cess', store=True, readonly=True, compute='_compute_amount')
    visible_cess = fields.Boolean(string='Cess',default=False)
    include = fields.Boolean(string='Inclusive')

    @api.multi
    def get_taxes_values(self):
        res=super(AccountInvoice, self).get_taxes_values()
        tax_grouped = {}
        if self.type == 'in_invoice':
            for line in self.invoice_line_ids:
                base_price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                disc_amt = line.scheme_discount_amount / line.quantity

                disc_per = (base_price * line.scheme_discount) / 100
                price_unit = base_price - disc_per - disc_amt

                if self.type in ['in_invoice', 'in_refund'] and self.include == True:
                    if line.cess_tax_id:
                        taxes = \
                        line.invoice_line_tax_ids.compute_cess_tax_include(price_unit, self.currency_id, line.quantity,
                                                                           line.product_id, self.partner_id,
                                                                           cess_tax_id=line.cess_tax_id)['taxes']
                    else:
                        taxes = \
                        line.invoice_line_tax_ids.compute_all_include(price_unit, self.currency_id, line.quantity,
                                                                      line.product_id,
                                                                      self.partner_id)['taxes']

                else:
                    if line.cess_tax_id:
                        taxes = line.invoice_line_tax_ids.compute_cess_tax(price_unit, self.currency_id, line.quantity,
                                                                           line.product_id, self.partner_id,
                                                                           cess_tax_id=line.cess_tax_id)['taxes']
                    else:
                        taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity,
                                                                      line.product_id,
                                                                      self.partner_id)['taxes']
                for tax in taxes:
                    val = self._prepare_tax_line_vals(line, tax)
                    key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                    if key not in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']
        else:
            for line in self.invoice_line_ids:

                price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                if self.type in ['in_invoice', 'in_refund'] and self.include == True:
                    if line.cess_tax_id:
                        taxes = \
                        line.invoice_line_tax_ids.compute_cess_tax_include(price_unit, self.currency_id, line.quantity,
                                                                           line.product_id, self.partner_id,
                                                                           cess_tax_id=line.cess_tax_id)['taxes']
                    else:
                        taxes = \
                        line.invoice_line_tax_ids.compute_all_include(price_unit, self.currency_id, line.quantity,
                                                                      line.product_id,
                                                                      self.partner_id)['taxes']

                else:
                    if line.cess_tax_id:
                        taxes = line.invoice_line_tax_ids.compute_cess_tax(price_unit, self.currency_id, line.quantity,
                                                                           line.product_id, self.partner_id,
                                                                           cess_tax_id=line.cess_tax_id)['taxes']
                    else:
                        taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity,
                                                                      line.product_id,
                                                                      self.partner_id)['taxes']
                for tax in taxes:
                    val = self._prepare_tax_line_vals(line, tax)
                    key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                    if key not in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']

        return tax_grouped

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id',
                     'date_invoice', 'type','invoice_line_ids.cess_amount','include')
    def _compute_amount(self):

        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        amount_tax = sum(line.amount for line in self.tax_line_ids)
        self.amount_cess = sum(line.cess_amount for line in self.invoice_line_ids)
        self.amount_tax = amount_tax - self.amount_cess
        self.amount_total = self.amount_untaxed + self.amount_tax+self.amount_cess
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
        return super(AccountInvoice, self)._compute_amount()