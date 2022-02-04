# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import UserError
from openerp.exceptions import UserError, ValidationError


class qlty_expense(models.Model):
    _name = 'qlty.expense'
    _description = " Expense"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type', 'in', ('bank', 'cash'))])

        return journal and journal[0] or False

    name = fields.Char(string='Expense Description', required=True)

    date = fields.Date(string='Date', default=fields.Date.context_today, required=True,
                       copy=False)

    is_petty = fields.Boolean(string='Petty Cash')


    employee_name = fields.Char(string="Employee")

    total = fields.Monetary(string=' Amount', required=True)

    product_id = fields.Many2one('product.product', string='Product')

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, default=lambda self: self.env.user.company_id.id)

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, default=_get_default_journal,
                                 domain=[('type', 'in', ('bank', 'cash'))])

    move_line_ids = fields.One2many('account.move.line', 'branchexp_id', copy=False, ondelete='restrict')

    account_move_id = fields.Many2one('account.move', string='Journal Entry', copy=False, track_visibility="onchange")

    state = fields.Selection([('draft', 'Unposted'), ('posted', 'Posted')], string='Status',
                             required=True, readonly=True, copy=False, default='draft',
                             help='All manually created new expense entries are usually in the status \'Unposted\', '
                                  'but you can set the option to skip that status on the related journal.')

    @api.multi
    def expense_move(self):

        if self.product_id:
            account = self.product_id.property_account_expense_id
            if not account:
                raise UserError(
                    _("No Expense account found for the product %s (or for it's category), please configure one.") % (
                        self.product_id.name))

        amount = -1 * self.total
        move = self._create_payment_entry_current(amount)
        self.state = 'posted'
        return

    def _create_payment_entry_current(self, amount):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False

        # if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
        #     # if all the invoices selected share the same currency, record the paiement in that currency too
        #     invoice_currency = self.invoice_ids[0].currency_id


        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id,
                                                  invoice_currency)

        move = self.env['account.move'].create(self._get_move_vals_current())

        # Write line corresponding to invoice payment



        counterpart_aml_dict = self._get_shared_move_line_vals_current(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals_current())
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals2_current(credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals_current(-amount))
        aml_obj.create(liquidity_aml_dict)

        move.post()
        self.write({'account_move_id': move.id})
        return move

    @api.one
    @api.constrains('total')
    def _check_values(self):
        if self.total == 0.0:
            raise Warning(_('Total should not be zero.'))

    def _get_move_vals_current(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'),
                            _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        name = journal.with_context(ir_sequence_date=self.date).sequence_id.next_by_id()
        return {

            'name': name,
            'date': self.date,
            #             'ref': self.voucher_no or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
        }

    def _get_shared_move_line_vals_current(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {

            # 'partner_id': self.env['res.partner']._find_accounting_partner(self.partner_id).id,
            #           'partner_id': self.employee_id.address_home_id.id if self.employee_id else False,
            # 'invoice_id': invoice_id and invoice_id.id or False,

            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
        }

    def _get_counterpart_move_line_vals_current(self):

        # if invoice:
        name = self.name + ' '

        #     for inv in invoice:
        #         if inv.move_id:
        #             name += inv.number + ', '
        #     name = name[:len(name) - 2]


        return {
            'name': name,
            'account_id': self.journal_id.default_debit_account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'branchexp_id': self.id,
        }

    def _get_shared_move_line_vals2_current(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {
            #             'partner_id': self.employee_id.address_home_id.id if self.employee_id else False,
            # 'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
        }

    def _get_liquidity_move_line_vals_current(self, amount):

        #         if invoice:
        name = 'Expense '

        # if self.invoice_ids:
        #     for inv in self.invoice_ids:
        #         if inv.move_id:
        #             name += inv.number + ', '


        #             for inv in invoice:
        #                 if inv.move_id:
        #                     name += inv.number + ', '
        #             name = name[:len(name)-2]

        vals = {
            'name': name,
            'account_id': self.product_id.property_account_expense_id.id,
            'branchexp_id': self.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.date).compute(amount,
                                                                           self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                date=self.date).compute_amount_fields(amount, self.journal_id.currency_id,
                                                      self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals


###################### For Current Brnach Other ###########################################################################


class AcoountMoveLines(models.Model):
    _inherit = 'account.move.line'

    branchexp_id = fields.Many2one('qlty.expense', string=" Expense",
                                   help="Expense that created this entry")


class product_expense(models.Model):
    _inherit = 'product.template'
    _name = 'product.template'

    expense_bool = fields.Boolean(string="Expense", default=False)


class product_expense(models.Model):
    _inherit = 'product.product'
    _name = 'product.product'

    expense_bool = fields.Boolean(string="Expense", related='product_tmpl_id.expense_bool')






