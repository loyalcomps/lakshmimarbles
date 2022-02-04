from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    cheque_payment_ids = fields.Many2many('cheque.payment', 'account_invoice_cheque_payment_rel', 'invoice_id', 'cheque_payment_id',
                                   string="Payments", copy=False, readonly=True)

class cheque_register_payments(models.TransientModel):
    _name = "cheque.register.payments"
    _inherit = 'cheque.abstract.payment'
    _description = "Cheque payments on multiple invoices"


    cheque_payable_account_id = fields.Many2one('account.account', string='Cheque Payable')
    bank_reference = fields.Char(copy=False)
    cheque_reference = fields.Char(copy=False)
    check_number = fields.Integer(string="Check Number", readonly=True, copy=False, default=0,
                                  help="Number of the check corresponding to this payment. If your pre-printed check are not already numbered, "
                                       "you can manage the numbering in the journal configuration page.")
    check_manual_sequencing = fields.Boolean(related='journal_id.check_manual_sequencing')

    # @api.onchange('payment_type')
    # def _onchange_payment_type(self):
    #     if self.payment_type:
    #         return {'domain': {'payment_method_id': [('payment_type', '=', self.payment_type)]}}

    def _get_invoices(self):
        return self.env['account.invoice'].browse(self._context.get('active_ids'))

    @api.model
    def default_get(self, fields):
        rec = super(cheque_register_payments, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_("Programmation error: wizard action executed without active_model or active_ids in context."))

        # Checks on received invoice records
        invoices = self.env[active_model].browse(active_ids)
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(_("You can only register payments for open bills"))
        if any(inv.type != 'in_invoice' for inv in invoices):
            raise UserError(_("You can only register payments for vendor bills"))
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(_("You can only register payments for open bills"))
        if any(inv.commercial_partner_id != invoices[0].commercial_partner_id for inv in invoices):
            raise UserError(_("In order to pay multiple bills at once, they must belong to the same commercial partner."))
        if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type] for inv in invoices):
            raise UserError(_("You cannot mix customer invoices and vendor bills in a single payment."))
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple bills at once, they must use the same currency."))

        total_amount = sum(inv.residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] for inv in invoices)
        communication = ' '.join([ref for ref in invoices.mapped('reference') if ref])

        rec.update({
            'amount': abs(total_amount),
            'currency_id': invoices[0].currency_id.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            # 'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'communication': communication,
        })
        return rec

    def get_payment_vals(self):
        """ Hook for extension """
        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            'invoice_ids': [(4, inv.id, None) for inv in self._get_invoices()],
            'payment_type': self.payment_type,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'bank_reference':self.bank_reference,
            'cheque_reference':self.cheque_reference,
            'check_manual_sequencing': self.check_manual_sequencing,
            # 'partner_type': self.partner_type,
        }

    @api.multi
    def create_payment(self):
        payment = self.env['cheque.payment'].create(self.get_payment_vals())
        payment.post()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def create_avoid_cheque(self):
        res = {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'payment_type': self.payment_type,
            'currency_id': self.currency_id.id,

        }
        payment = self.env['cheque.payment'].create(res)
        payment.avoid_cheque()
        return {'type': 'ir.actions.act_window_close'}

    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if not self.amount > 0.0:
            raise ValidationError(_('The payment amount must be strictly positive.'))

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id.check_manual_sequencing:
            self.check_number = self.journal_id.check_sequence_id.number_next_actual
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

    #To compute total invoice amount

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


