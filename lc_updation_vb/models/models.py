# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_invoice_open(self):
        super(AccountInvoice, self).action_invoice_open()

        for record in self:
            if record.type == 'in_invoice':

                for line in record.invoice_line_ids:
                    line.product_id.landing_cost = line.landing_cost