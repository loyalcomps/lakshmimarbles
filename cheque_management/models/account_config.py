from odoo import api,fields,models

class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    cheque_payable_account_id = fields.Many2one('account.account',
        domain=lambda self: [('reconcile', '=', True), ('user_type_id.id', '=',
        self.env.ref('account.data_account_type_payable').id)],
        help="Intermediary account used cheque payment",string="Cheque Payable")

    @api.multi
    def set_Cheque_payable_account(self):
        """ Set the product taxes if they have changed """
        ir_values_obj = self.env['ir.values']
        ir_values_obj.sudo().set_default('account.config.settings', "cheque_payable_account_id",
                                        self.cheque_payable_account_id.id )
        # ir_values_obj.sudo().set_default('cheque.payment', "cheque_payable_account_id",
        #                                  [self.cheque_payable_account_id.id] if self.cheque_payable_account_id else False,
        #                                  for_all_users=True, company_id=self.company_id.id)
        # ir_values_obj.sudo().set_default('cheque.register.payments', "cheque_payable_account_id",
        #                                  [
        #                                      self.cheque_payable_account_id.id] if self.cheque_payable_account_id else False,
        #                                  for_all_users=True, company_id=self.company_id.id)

