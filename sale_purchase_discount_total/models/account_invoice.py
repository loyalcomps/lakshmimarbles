from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"



    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='percent')
    discount_rate = fields.Float('Discount Amount', digits=(16, 2), readonly=True, states={'draft': [('readonly', False)]})
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_compute_amount',
                                      track_visibility='always')

    discount_amt = fields.Float(string="Discount", digits=dp.get_precision('Discount'), default=0.0, store=True)

    @api.onchange('discount_type','discount_rate')
    def _onchange_discount(self):
        disc_amount = 0
        if (self.amount_untaxed + self.amount_tax) > 0:
            if self.discount_type == "amount":
                if self.discount_rate >= self.amount_untaxed + self.amount_tax:
                    raise UserError(('Cannot give discount more than total amount.'))
                self.discount_amt = self.discount_rate
            if self.discount_type == "percent":
                disc_amount = ((self.amount_untaxed + self.amount_tax) * self.discount_rate) / 100
                if disc_amount >= self.amount_untaxed + self.amount_tax:
                    raise UserError(('Cannot give discount more than total amount.'))
                self.discount_amt = disc_amount

    @api.one
    @api.depends('discount_amt')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        self.amount_total = (self.amount_total - self.discount_amt) if (self.amount_untaxed + self.amount_tax) > 0 else self.amount_total
        amount_total_company_signed = self.amount_total
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_discount = self.discount_amt if (self.amount_untaxed + self.amount_tax) > 0 else 0

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        ir_values = self.env['ir.values']
        if (self.amount_untaxed + self.amount_tax) > 0 and self.discount_amt:
            if self.type in ('in_invoice','in_refund'):

                disc_id = ir_values.get_default('account.config.settings', 'purchase_discount_account',company_id=self.company_id.id)
                move_line_dict = {
                    'type': 'dest',
                    'name': 'Purchase Discount',
                    'price_unit': self.discount_amt,
                    'price': -self.discount_amt,
                    'account_id': disc_id,
                    'invoice_id': self.id,
                }
            else:
                disc_id = ir_values.get_default('account.config.settings', 'sale_discount_account',company_id=self.company_id.id)
                move_line_dict = {
                    'type': 'dest',
                    'name': 'Sale Discount',
                    'price_unit': self.discount_amt,
                    'price': -self.discount_amt,
                    'account_id': disc_id,
                    'invoice_id': self.id,
                }

            res.append(move_line_dict)

        return res

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice, date, description, journal_id)
        values['discount_type'] = invoice.discount_type
        values['discount_rate'] = invoice.discount_rate
        values['discount_amt'] = invoice.discount_amt
        return values