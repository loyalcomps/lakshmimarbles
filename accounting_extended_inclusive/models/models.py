# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountTax(models.Model):
    _inherit = 'account.tax'

    def _compute_amount_inc(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        # res = super(AccountTax, self)._compute_amount_inc(base_amount, price_unit, quantity, product, partner)
        self.ensure_one()
        if 'price_include' in self.env.context:
            price_include = True

            if (self.amount_type == 'percent' and not price_include) or (
                    self.amount_type == 'division' and price_include):
                return base_amount * self.amount / 100
            if self.amount_type == 'percent' and price_include:
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


            if self.amount_type == 'division' and not price_include:
                return base_amount / (1 - self.amount / 100) - base_amount

class AccountInvoice(models.Model):
    _inherit='account.invoice'

    @api.multi
    def get_taxes_values(self):
        res = super(AccountInvoice, self).get_taxes_values()
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            if self.inclusive:
                taxes = line.invoice_line_tax_ids.with_context(price_include=True,include_base_amount=True).compute_all_inc(price_unit, self.currency_id, line.quantity, line.product_id,
                                                          self.partner_id)['taxes']
            else:
                taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
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

    @api.multi
    def get_hsn_taxes_values(self):
        tax_hsn_grouped = {}
        tax_grouped = {}
        for line in self.invoice_line_ids:
            hsn = line.product_id.x_hsn_code
            hsnVal = hsn
            if not hsnVal:
                hsnVal = 'false'
            if hsnVal not in tax_hsn_grouped:
                tax_hsn_grouped[hsnVal] = {}
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if self.inclusive:
                taxes = line.invoice_line_tax_ids.with_context(price_include=True,include_base_amount=True).compute_all_inc(price_unit, self.currency_id, line.quantity, line.product_id,
                                                          self.partner_id)['taxes']
            else:
                taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
                                                          self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
                if key not in tax_hsn_grouped[hsnVal]:
                    val['hsn_code'] = hsn
                    tax_hsn_grouped[hsnVal][key] = val
                else:
                    tax_hsn_grouped[hsnVal][key]['amount'] += val['amount']
                    tax_hsn_grouped[hsnVal][key]['base'] += val['base']
        return tax_hsn_grouped