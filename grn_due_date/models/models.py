# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    gr_date = fields.Date(string='GR Date',
                           readonly=True, states={'draft': [('readonly', False)]}, index=True, copy=False)

    @api.onchange('gr_date','payment_term_id','date_invoice')
    def _onchange_payment_term_date_invoice(self):
        if self.type in ('in_invoice','in_refund'):
            date = self.gr_date
            if not date:
                date = fields.Date.context_today(self)
                self.gr_date =date
            if not self.payment_term_id:
                # When no payment term defined
                self.date_due = self.date_due or self.gr_date
            else:
                pterm = self.payment_term_id
                pterm_list = \
                pterm.with_context(currency_id=self.company_id.currency_id.id).compute(value=1, date_ref=date)[0]
                self.date_due = max(line[0] for line in pterm_list)
        else:
            super(AccountInvoice, self)._onchange_payment_term_date_invoice()

#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100