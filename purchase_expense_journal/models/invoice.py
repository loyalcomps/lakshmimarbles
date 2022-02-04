# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError



class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    purchase_expense_line_ids = fields.One2many('invoice.expense', 'invoice_id', string='Purchase Expense',
                                                readonly=True, states={'draft': [('readonly', False)]} )
    expense = fields.Monetary(string="Purchase Expense", store=True, readonly=True, track_visibility='always',
                                     compute="_compute_amount")
    expense_move_id = fields.Many2one('account.move', string='Expense Journal Entry',
                              readonly=True, index=True,  copy=False,
                              help="Link to the automatically generated expense Journal Items.")

    @api.depends('purchase_expense_line_ids')
    def compute_total_expense(self):
        for order in self:
            expense = 0
            for line in order.purchase_expense_line_ids:
                expense += line.rate
                order.update({
                    'total_expense': expense
                })

    total_expense = fields.Float(string="Total Expense", store=True, compute="compute_total_expense")


    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        new_lines = self.env['invoice.expense']
        for line in self.purchase_id.purchase_expense_line_ids:
            data = {
                'name': line.name,
                'company_id': line.company_id.id,
                'rate': line.rate,
                'exp_to_total':line.exp_to_total,
            }
            new_line = new_lines.new(data)
            new_lines += new_line

        self.purchase_expense_line_ids += new_lines
        return super(AccountInvoice, self).purchase_order_change()


    @api.one
    @api.depends('purchase_expense_line_ids')
    def _compute_amount(self):
        res = super(AccountInvoice, self)._compute_amount()
        expense = 0
        if self.type in ['in_invoice', 'in_refund']:

            for line in self.purchase_expense_line_ids:
                expense += line.rate if line.exp_to_total == True else 0
            self.amount_total = self.amount_total+expense
            self.expense = expense

            amount_total_company_signed = self.amount_total

            if self.currency_id and self.currency_id != self.company_id.currency_id:
                currency_id = self.currency_id.with_context(date=self.date_invoice)
                amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)

            sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
            self.amount_total_company_signed = amount_total_company_signed * sign
            self.amount_total_signed = self.amount_total * sign

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        ir_values = self.env['ir.values']
        for line in self.purchase_expense_line_ids:
            if line.name == 'freight' and line.exp_to_total == True:
                disc_id = ir_values.get_default('account.config.settings', 'freight_account_purchase')
                move_line_dict = {
                    'type': 'dest',
                    'name': 'Purchase Freight Charge',
                    'price_unit': line.rate,
                    'price': line.rate,
                    'account_id': disc_id,
                    'invoice_id': self.id,
                }

                res.append(move_line_dict)

            if line.name == 'union' and line.exp_to_total == True:
                disc_id = ir_values.get_default('account.config.settings', 'union_account')
                move_line_dict = {
                    'type': 'dest',
                    'name': 'Purchase Union Charge',
                    'price_unit': line.rate,
                    'price': line.rate,
                    'account_id': disc_id,
                    'invoice_id': self.id,
                }

                res.append(move_line_dict)


            if line.name == 'packing' and line.exp_to_total == True:
                disc_id = ir_values.get_default('account.config.settings', 'packing_account')
                move_line_dict = {
                    'type': 'dest',
                    'name': 'Purchase Packing Charge',
                    'price_unit': line.rate,
                    'price': line.rate,
                    'account_id': disc_id,
                    'invoice_id': self.id,
                }
                res.append(move_line_dict)

            if line.name == 'other' and line.exp_to_total == True:
                disc_id = ir_values.get_default('account.config.settings', 'other_account')
                move_line_dict = {
                    'type': 'dest',
                    'name': 'Purchase Other Charge',
                    'price_unit': line.rate,
                    'price': line.rate,
                    'account_id': disc_id,
                    'invoice_id': self.id,
                }
                res.append(move_line_dict)



        return res

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice, date, description, journal_id)
        values['purchase_expense_line_ids'] = self._refund_cleanup_lines(invoice.purchase_expense_line_ids)
        return values

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        for record in self:
            expenses = record.purchase_expense_line_ids.filtered(lambda exp: exp.exp_to_total != True)
            expense_amt =0
            expe=[]
            if expenses:
                for exp in expenses:
                    expense_amt += exp.rate
                    expe.append(exp.id)

                text = """Do you want to pay expenses which are not included in Total."""
                value = self.env['expense.validate.confirm'].sudo().create({'text': text,
                                 'amount':expense_amt,})
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Message',
                    'res_model': 'expense.validate.confirm',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'inv_obj': record.id, 'amount': expense_amt,'expenses':expe},
                    'res_id': value.id
                    }

    @api.multi
    def action_cancel(self):
        res =super(AccountInvoice, self).action_cancel()
        moves = self.env['account.move']
        for inv in self:
            if inv.expense_move_id:
                moves += inv.expense_move_id

        # First, set the invoices as cancelled and detach the move ids
        self.write({'expense_move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        return res
class InvoiceExpense(models.Model):
    _name = 'invoice.expense'


    invoice_id = fields.Many2one('account.invoice', string='Invoice', ondelete='cascade',)
    name = fields.Selection([
            ('freight', 'Freight Charge'),
            ('union', 'Union Charge'),
            ('packing', 'Packing Charge'),
        ('other','Other Charges'),
        ], string='Expense', required=True,)
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env['res.company']._company_default_get('invoice.expense'))

    rate = fields.Float(string = 'Amount',digits=dp.get_precision('Discount'),default=0.0)
    exp_to_total = fields.Boolean(string='Expense to Toal', default=True, help='Expense to Toal')

# class AccountInvoiceLine(models.Model):
#     _inherit = "account.invoice.line"
#
#     @api.depends('invoice_id.purchase_expense_line_ids')
#     def get_landing_cost(self):
#         res=super(AccountInvoiceLine, self).get_landing_cost()
#         expense = 0
#
#         for line in self:
#             expense = line.invoice_id.total_expense
#             total_amount = line.invoice_id.amount_untaxed + line.invoice_id.amount_tax
#             line_expense = (expense * line.price_subtotal_taxinc) / (total_amount * line.quantity) if (total_amount * line.quantity) != 0 else 0
#
#             line.landing_cost += line_expense
#             line.margin = line.product_mrp - line.landing_cost
#             line.margin_per = (line.margin / line.product_mrp) * 100 if line.product_mrp else 0

class ExpenseValidateConfirmation(models.TransientModel):
    _name = 'expense.validate.confirm'

    text=fields.Text()
    choice = fields.Selection([('yes','Yes'),('no','No')])
    journal_id = fields.Many2one('account.journal', string='Payment Journal',
                                 domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type',
                                        oldname="payment_method")
    payment_method_code = fields.Char(related='payment_method_id.code',
                                      help="Technical field used to adapt the interface to the payment type selected.",
                                      readonly=True)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
                                         help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")
    payment_reference = fields.Char(string='Reference',help="Reference of the document used to issue this payment. Eg. check number, file name, etc.")
    narration = fields.Char(string='Narration')

    @api.one
    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        if not self.journal_id:
            self.hide_payment_method = True
            return
        journal_payment_methods = self.journal_id.outbound_payment_method_ids
        self.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = 'outbound'
            return {'domain': {
                'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
        return {}

    def validate_expense(self):
        for record in self:
            if record.choice=='yes':
                account_move = self.env['account.move']


                if not record.journal_id.sequence_id:
                    raise UserError(_('Please define sequence on the journal'))

                res=[]
                ir_values = self.env['ir.values']


                for line in record.env.context['expenses']:
                    exp = self.env['invoice.expense'].browse(line)
                    if exp.name == 'freight' :
                        disc_id = ir_values.get_default('account.config.settings', 'freight_account')
                        move_line_dict = {
                            'type': 'dest',
                            'name': 'Purchase Freight Charge',
                            'price_unit': exp.rate,
                            'price': exp.rate,
                            'account_id': disc_id,
                            # 'invoice_id': self.id,
                        }

                        res.append(move_line_dict)

                    if exp.name == 'union' :
                        disc_id = ir_values.get_default('account.config.settings', 'union_account')
                        move_line_dict = {
                            'type': 'dest',
                            'name': 'Purchase Union Charge',
                            'price_unit': exp.rate,
                            'price': exp.rate,
                            'account_id': disc_id,
                            # 'invoice_id': self.id,
                        }

                        res.append(move_line_dict)

                    if exp.name == 'packing':
                        disc_id = ir_values.get_default('account.config.settings', 'packing_account')
                        move_line_dict = {
                            'type': 'dest',
                            'name': 'Purchase Packing Charge',
                            'price_unit': exp.rate,
                            'price': exp.rate,
                            'account_id': disc_id,
                            # 'invoice_id': self.id,
                        }
                        res.append(move_line_dict)

                    if exp.name == 'other' :
                        disc_id = ir_values.get_default('account.config.settings', 'other_account')
                        move_line_dict = {
                            'type': 'dest',
                            'name': 'Purchase Other Charge',
                            'price_unit': exp.rate,
                            'price': exp.rate,
                            'account_id': disc_id,
                            # 'invoice_id': self.id,
                        }
                        res.append(move_line_dict)


                name = record.journal_id.with_context(ir_sequence_date=record.payment_date).sequence_id.next_by_id() or '/'
                res.append({
                    'type': 'dest',
                    'name': name,
                    'price': -1*record.amount,
                    'account_id': record.journal_id.default_credit_account_id.id,
                    'date_maturity': record.payment_date,
                    # 'amount_currency': diff_currency and total_currency,
                    'currency_id': record.currency_id.id,
                    # 'invoice_id': inv.id
                })
                line = [(0, 0, record.line_get_convert(l)) for l in res]
                move_vals = {
                    'ref': record.payment_reference,
                    'line_ids': line,
                    'journal_id': record.journal_id.id,
                    'date': record.payment_date,
                    'narration': record.narration,
                }
                move = account_move.create(move_vals)

                move.post()

                inv = self.env['account.invoice'].browse(record.env.context['inv_obj'])
                inv.write({'expense_move_id':move.id})


    @api.model
    def line_get_convert(self, line):
        return {
            'date_maturity': line.get('date_maturity', False),
            'name': line['name'],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'currency_id': line.get('currency_id', False),

        }
