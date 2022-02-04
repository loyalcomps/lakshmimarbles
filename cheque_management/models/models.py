# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class cheque_abstract_payment(models.AbstractModel):
    _name = "cheque.abstract.payment"
    _description = "Contains the logic shared between models which allows to register cheque payments"

    payment_type = fields.Selection([('outbound', 'Send Money')], string='Payment Type', default='outbound',
                                    )
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True,
                                        oldname="payment_method", domain=[('code', '=', 'check_printing')])
    payment_method_code = fields.Char(related='payment_method_id.code',
                                      help="Technical field used to adapt the interface to the payment type selected.",
                                      readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', domain=[('supplier', '=', True)])
    amount = fields.Monetary(string='Payment Amount', default=0)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    communication = fields.Char(string='Memo')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', '=', 'bank')])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)

    @api.one
    @api.constrains('amount')
    def _check_amount(self):

        if not self.amount > 0.0 and self.state not in ('draft','avoid'):
            raise ValidationError(_('The payment amount must be strictly positive.'))

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods.search(
                [('code', '=', 'check_printing')]) or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type
            return {'domain': {
                'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids),
                                      ('code', '=', 'check_printing')]}}
        return {}

    def _get_invoices(self):
        """ Return the invoices of the payment. Must be overridden """
        raise NotImplementedError

        # To compute total invoice amount

    def _compute_total_invoices_amount(self):
        """ Compute the sum of the residual of invoices, expressed in the payment currency """
        payment_currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or self.env.user.company_id.currency_id
        invoices = self._get_invoices()

        if all(inv.currency_id == payment_currency for inv in invoices):
            total = sum(invoices.mapped('residual_signed'))
        else:
            total = 0
            for inv in invoices:
                if inv.company_currency_id != payment_currency:
                    total += inv.company_currency_id.with_context(date=self.payment_date).compute(
                        inv.residual_company_signed, payment_currency)
                else:
                    total += inv.residual_company_signed
        return abs(total)


class ChequePayment(models.Model):
    _name = "cheque.payment"
    _inherit = 'cheque.abstract.payment'
    _description = "Cheque Payments"
    _order = "payment_date desc, name desc"

    cheque_payable_account_id = fields.Many2one('account.account',domain=lambda self: [('reconcile', '=', True), ('user_type_id.id', '=',
        self.env.ref('account.data_account_type_payable').id)],string="Cheque Payable")
    reason = fields.Text()

    @api.one
    @api.depends('invoice_ids')
    def _get_has_invoices(self):
        self.has_invoices = bool(self.invoice_ids)

    @api.one
    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        if len(self.invoice_ids) == 0:
            return
        if self.invoice_ids[0].type in ['in_invoice']:
            self.payment_difference = self.amount - self._compute_total_invoices_amount()
        else:
            self.payment_difference = self._compute_total_invoices_amount() - self.amount


    def _get_invoices(self):
        return self.invoice_ids



    name = fields.Char(readonly=True, copy=False, default="Draft Payment")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('printed', 'Printed'),
        ('sent_approval', 'Sent for Approval'),
        ('approved', 'Approved'),
        ('sent_signature', 'Sent for Signature'),
        ('ready_release', 'Ready to Release'),
        ('release', 'Release'),
        ('cancel', 'Cheque Cancelled'),
        ('avoid', 'Avoid')
    ], readonly=True, default='draft', copy=False, string="Status")

    check_manual_sequencing = fields.Boolean(related='journal_id.check_manual_sequencing', readonly=1)
    check_number = fields.Integer(string="Cheque Number", readonly=True, copy=False,
                                  help="The selected journal is configured to print check numbers. If your pre-printed check paper already has numbers "
                                       "or if the current numbering is wrong, you can change it in the journal configuration page.")
    bank_reference = fields.Char(copy=False)
    cheque_reference = fields.Char(copy=False)

    payment_reference = fields.Char(copy=False, readonly=True,
                                    help="Reference of the document used to issue this payment. Eg. check number, file name, etc.")
    move_name = fields.Char(string='Journal Entry Name', readonly=True,
                            default=False, copy=False,
                            help="Technical field holding the number given to the journal entry, automatically set when the statement line is reconciled then stored to set the same number again if the line is cancelled, set to draft and re-processed again.")

    destination_account_id = fields.Many2one('account.account', compute='_compute_destination_account_id',
                                             readonly=True)
    destination_journal_id = fields.Many2one('account.journal', string='Transfer To',
                                             domain=[('type', '=', 'bank')])

    invoice_ids = fields.Many2many('account.invoice', 'account_invoice_cheque_payment_rel', 'cheque_payment_id', 'invoice_id',
                                   string="Invoices", copy=False, readonly=True)
    has_invoices = fields.Boolean(compute="_get_has_invoices", help="Technical field used for usability purposes")
    payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True)
    payment_difference_handling = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid')],
                                                   default='open', string="Payment Difference", copy=False)
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account",
                                          domain=[('deprecated', '=', False)], copy=False)
    # FIXME: ondelete='restrict' not working (eg. cancel a bank statement reconciliation with a payment)
    move_line_ids = fields.One2many('account.move.line', 'cheque_payment_id', readonly=True, copy=False, ondelete='restrict')

    @api.model
    def create(self, vals):
        if 'check_manual_sequencing' in vals:
            seq=vals.get('check_manual_sequencing')
        else:
            seq = self.env['account.journal'].browse(vals['journal_id']).check_manual_sequencing

        if vals['payment_method_id'] == self.env.ref('account_check_printing.account_payment_method_check').id and seq:
            sequence = self.env['account.journal'].browse(vals['journal_id']).check_sequence_id
            vals.update({'check_number': sequence.next_by_id()})
        return super(ChequePayment, self).create(vals)

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_id')
    def _compute_destination_account_id(self):
        if self.invoice_ids:
            self.destination_account_id = self.invoice_ids[0].account_id.id

        elif self.partner_id:
            self.destination_account_id = self.partner_id.property_account_payable_id.id





    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if hasattr(super(ChequePayment, self), '_onchange_journal_id'):
            super(ChequePayment, self)._onchange_journal_id()
        if self.journal_id.check_manual_sequencing:
            self.check_number = self.journal_id.check_sequence_id.number_next_actual

    @api.model
    def default_get(self, fields):
        rec = super(ChequePayment, self).default_get(fields)
        ir_values = self.env['ir.values']
        acc_id = ir_values.get_default('account.config.settings', 'cheque_payable_account_id')
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec['communication'] = invoice['reference'] or invoice['name'] or invoice['number']
            rec['currency_id'] = invoice['currency_id'][0]
            rec['payment_type'] = invoice['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['partner_id'] = invoice['partner_id'][0]
            rec['amount'] = invoice['residual']
        rec['cheque_payable_account_id'] =acc_id
        return rec

    @api.multi
    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('cheque_payment_id', 'in', self.ids)],
        }

    @api.multi
    def unlink(self):
        if any(bool(rec.move_line_ids) for rec in self):
            raise UserError(_("You can not delete a payment that is already posted"))
        if any(rec.move_name for rec in self):
            raise UserError(_(
                'It is not allowed to delete a payment that already created a journal entry since it would create a gap in the numbering. You should create the journal entry again and cancel it thanks to a regular revert.'))
        return super(ChequePayment, self).unlink()

    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'printed'.
            A journal entry is created containing an item in the source liquidity account (selected cheque payable account)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.

        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(
                    _("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)
            if not rec.cheque_payable_account_id:
                raise UserError(_('Configuration Error !'),
                                _('You have to assign cheque payable COA in your company account settings.') )
            if not rec.partner_id:
                raise UserError(_('Please choose a partner to post the payment.') )
            if not rec.amount>0:
                raise ValidationError(_('The payment amount must be strictly positive.'))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                'cheque.payment.supplier.invoice')
            if not rec.name :
                raise UserError(_("You have to define a sequence for Cheque Payment in your company."))
            # Create the journal entry
            amount = rec.amount *  1
            move = rec._create_payment_entry(amount)
            rec.write({'state': 'printed', 'move_name': move.name})

    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            # if all the invoices selected share the same currency, record the payement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id,
                                                          invoice_currency)

        move = self.env['account.move'].create(self._get_move_vals())

        # Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        # Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(
                self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
            # the writeoff debit and credit must be computed from the invoice residual in company currency
            # minus the payment amount in company currency, and not from the payment difference in the payment currency
            # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
            total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
            total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount,
                                                                                                         self.company_id.currency_id)
            if self.invoice_ids[0].type == 'in_invoice':
                amount_wo = total_payment_company_signed - total_residual_company_signed

            # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
            # amount in the company currency
            if amount_wo > 0:
                debit_wo = amount_wo
                credit_wo = 0.0
                amount_currency_wo = abs(amount_currency_wo)
            else:
                debit_wo = 0.0
                credit_wo = -amount_wo
                amount_currency_wo = -abs(amount_currency_wo)
            writeoff_line['name'] = _('Counterpart')
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit']:
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit']:
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo
        if self.state != 'ready_release':
            self.invoice_ids.register_payment(counterpart_aml)
        if self.state == 'ready_release':
            counterpart_aml.reconcile(writeoff_acc_id=False, writeoff_journal_id=False)


        # Write counterpart lines
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        aml_obj.create(liquidity_aml_dict)

        move.post()
        return move

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'),
                            _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        name = self.move_name or journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()
        return {
            'name': name,
            'date': self.payment_date,
            'ref': self.communication or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
        }

    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {
            'partner_id': self.partner_id and self.env[
                'res.partner']._find_accounting_partner(self.partner_id).id or False,
            'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
        }

    def _get_counterpart_move_line_vals(self, invoice=False):
        name = _("Vendor Payment")

        if invoice:
            name += ': '
            for inv in invoice:
                if inv.move_id:
                    name += inv.number + ', '
            name = name[:len(name) - 2]
        if self.state == 'draft':
            account_id = self.destination_account_id.id
        if self.state == 'ready_release':
            account_id = self.cheque_payable_account_id.id
        return {
            'name': name,
            'account_id': account_id ,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'cheque_payment_id': self.id,
        }

    def _get_liquidity_move_line_vals(self, amount):
        name = self.name
        if self.state == 'draft':
            account_id = self.cheque_payable_account_id.id
        if self.state == 'ready_release':
            account_id = self.journal_id.default_credit_account_id.id

        vals = {
            'name': name,
            'account_id': account_id,
            'cheque_payment_id': self.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id,
                                                              self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals

    # End of posting of cheque

    # send for approval
    @api.multi
    def send_for_approval(self):
        for rec in self:
            rec.write({'state': 'sent_approval'})

    # approval of cheque
    @api.multi
    def approve_cheque(self):
        for rec in self:
            rec.write({'state': 'approved'})

    # sent signature process
    @api.multi
    def send_for_signature(self):
        for rec in self:
            rec.write({'state':'sent_signature'})

    # ready to release process
    @api.multi
    def ready_to_release(self):
        for rec in self:
            rec.write({'state': 'ready_release'})

    @api.multi
    def create_avoid_cheque(self):
        # res = {
        #     'journal_id': self.journal_id.id,
        #     'payment_method_id': self.payment_method_id.id,
        #     'payment_date': self.payment_date,
        #     'payment_type': self.payment_type,
        #     'currency_id': self.currency_id.id,
        #     'partner_id':False,
        #     'amount':0,
        # }
        # payment = self.create(res)
        # payment.avoid_cheque()
        for rec in self:
            rec.write({
                'partner_id':False,
                'amount':0,
                'state': 'avoid',
            })

    @api.multi
    def avoid_cheque(self):
        # avoid cheque process
        for rec in self:
            rec.write({'state': 'avoid'})

    @api.multi
    def set_to_draft(self):
        # set to draft
        for rec in self:
            rec.write({'state': 'draft'})

    @api.multi
    def cancel_cheque(self):
        # cancel cheque
        for rec in self:
            text = """Are you sure you want to cancel this cheque? If yes, plesae enter the reason below """
            query = 'delete from cheque_confirm_cancel_window'
            rec.env.cr.execute(query)
            value = rec.env['cheque.confirm.cancel.window'].sudo().create({'text': text})
            return {
                'type': 'ir.actions.act_window',
                'name': 'Cheque Cancellation',
                'res_model': 'cheque.confirm.cancel.window',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'cheque_obj': rec.id,},
                'res_id': value.id
            }
        # for rec in self:
        #     for move in rec.move_line_ids.mapped('move_id'):
        #         if rec.invoice_ids:
        #             move.line_ids.remove_move_reconcile()
        #         move.button_cancel()
        #         move.unlink()
        #     rec.state = 'cancel'
            # rec.write({'state': 'cancel'})





    #changing status to release and jour
    @api.multi
    def release_cheque(self):
        """ Create the journal items for the release payment and update the payment's state to 'release'.
                    A journal entry is created containing an item in the source liquidity account (cheque payable)
                    and another in the destination reconciliable account (journal credit account).
                    If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.

                """
        for rec in self:
            # Create the journal entry
            amount = rec.amount * 1
            move = rec._create_payment_entry(amount)
            move_name = rec.move_name+" "+move.name
            rec.write({'state': 'release', 'move_name': move_name})
            pass




class ChequeCancelWindow(models.Model):
    _name = 'cheque.confirm.cancel.window'

    text=fields.Text()
    reason = fields.Text()

    def cancel_cheque(self):
        if self.env.context['cheque_obj']:
            cheque_obj=self.env['cheque.payment'].browse(self.env.context['cheque_obj'])

            for rec in cheque_obj:
                for move in rec.move_line_ids.mapped('move_id'):
                    if rec.invoice_ids:
                        move.line_ids.remove_move_reconcile()
                    move.button_cancel()
                    move.unlink()
                rec.write({'state': 'cancel','reason':self.reason})
                # rec.state = 'cancel'

            pass