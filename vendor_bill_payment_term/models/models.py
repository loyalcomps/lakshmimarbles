# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    purchase_payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', oldname='payment_term',
        readonly=True, states={'draft': [('readonly', False)]},
        help="If you use payment terms, the due date will be computed automatically at the generation "
             "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "
             "The payment term may compute several due dates, for example 50% now, 50% in one month.")

    # @api.onchange('purchase_id')
    # def purchase_order_change(self):
    #     if not self.purchase_id:
    #         return {}
    #     if not self.payment_term_id:
    #         self.payment_term_id = self.purchase_id.payment_term_id.id
    #
    #     res = super(AccountInvoice, self).purchase_order_change()
    #     return res
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id
        if not self.purchase_payment_term_id :
            self.purchase_payment_term_id = self.purchase_id.payment_term_id.id if self.purchase_id.payment_term_id.id else False

        new_lines = self.env['account.invoice.line']
        for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_line(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.purchase_id = False
        return {}

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.type in ['in_invoice', 'in_refund']:
            if self.purchase_payment_term_id:
                self.payment_term_id = self.purchase_payment_term_id.id