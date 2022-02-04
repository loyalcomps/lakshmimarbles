from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    cheque_payment_id = fields.Many2one('cheque.payment', string="Originator Payment", help="Payment that created this entry")

class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.one
    def _set_check_next_number(self):
        if self.check_next_number < self.check_sequence_id.number_next_actual:
            payment_obj=self.env['account.payment'].search([('check_number','=',self.check_next_number),('journal_id.id','=',self.id)])
            cheque_obj = self.env['cheque.payment'].search([('check_number','=',self.check_next_number),('journal_id.id','=',self.id)])
            if payment_obj or cheque_obj:
                raise ValidationError(_(" %s is a used one. In order to avoid a check being rejected "
                                    "by the bank, you can only use a greater number.") % self.check_next_number)
        if self.check_sequence_id:
            self.check_sequence_id.sudo().number_next_actual = self.check_next_number