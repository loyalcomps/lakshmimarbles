# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from  odoo.exceptions import UserError
from odoo.tools.misc import formatLang

class AccountBankStatement(models.Model):


    @api.multi
    def _get_opening_balance(self, journal_id):
        return 0

    _inherit = "account.bank.statement"

    @api.multi
    def _balance_check(self):
        for stmt in self:
            if not stmt.currency_id.is_zero(stmt.difference):
                if stmt.journal_type == 'cash':
                    if stmt.difference < 0.0:
                        account = stmt.journal_id.loss_account_id
                        name = _('Loss')
                    else:
                        # statement.difference > 0.0
                        account = stmt.journal_id.profit_account_id
                        name = _('Profit')
                    if not account:
                        raise UserError(
                            _('There is no account defined on the journal %s for %s involved in a cash difference.') % (
                            stmt.journal_id.name, name))

                    values = {
                        'partner_id': stmt.user_id.partner_id.id,
                        'statement_id': stmt.id,
                        'account_id': account.id,
                        'amount': stmt.difference,
                        'name': _("Cash difference observed during the counting (%s)") % name,
                    }
                    self.env['account.bank.statement.line'].create(values)
                else:
                    balance_end_real = formatLang(self.env, stmt.balance_end_real, currency_obj=stmt.currency_id)
                    balance_end = formatLang(self.env, stmt.balance_end, currency_obj=stmt.currency_id)
                    raise UserError(_(
                        'The ending balance is incorrect !\nThe expected balance (%s) is different from the computed one. (%s)')
                                    % (balance_end_real, balance_end))
        return True
