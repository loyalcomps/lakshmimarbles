# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError



class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    purchase_expense_line_ids = fields.One2many('purchase.expense', 'invoice_id', string='Purchase Expense',
                                                readonly=True, states={'draft': [('readonly', False)]} )
    expense = fields.Monetary(string="Purchase Expense", store=True, readonly=True, track_visibility='always',
                                     compute="_compute_amount")

    @api.one
    @api.depends('purchase_expense_line_ids')
    def _compute_amount(self):
        res = super(AccountInvoice, self)._compute_amount()
        expense=0
        if self.type in ['in_invoice', 'in_refund']:
            for line in self.purchase_expense_line_ids:
                expense += line.rate
            self.amount_total = self.amount_total+expense
            self.expense = expense

            amount_total_company_signed = self.amount_total

            if self.currency_id and self.currency_id != self.company_id.currency_id:
                currency_id = self.currency_id.with_context(date=self.date_invoice)
                amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)

            sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
            self.amount_total_company_signed = amount_total_company_signed * sign
            self.amount_total_signed = self.amount_total * sign

    # @api.multi
    # def action_move_create(self):
    #
    #     account_move = self.env['account.move']
    #
    #     for inv in self:
    #
    #         if not inv.journal_id.sequence_id:
    #             raise UserError(_('Please define sequence on the journal related to this invoice.'))
    #         if not inv.invoice_line_ids:
    #             raise UserError(_('Please create some invoice lines.'))


class PurchaseExpense(models.Model):
    _name = 'purchase.expense'


    invoice_id = fields.Many2one('account.invoice', string='Invoice', ondelete='cascade',)
    name = fields.Selection([
            ('freight', 'Freight Charge'),
            ('union', 'Union Charge'),
            ('packing', 'Packing Charge'),
        ('other','Other Charges'),
        ], string='Expense', required=True,)
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env['res.company']._company_default_get('purchase.expense'))

    rate = fields.Float(string = 'Amount',digits=dp.get_precision('Discount'),default=0.0)

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.depends('invoice_id.purchase_expense_line_ids')
    def get_landing_cost(self):
        res=super(AccountInvoiceLine, self).get_landing_cost()
        expense = 0
        expense_pdct=0
        qty = 0
        for line in self:
            qty += line.quantity

        for invoice_line in self:
            for line in invoice_line.invoice_id.purchase_expense_line_ids:
                expense += line.rate
        if qty != 0:
            expense_pdct = expense / qty

        for line in self:

            line.landing_cost+=expense_pdct
