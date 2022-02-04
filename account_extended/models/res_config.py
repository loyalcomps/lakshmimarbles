# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class RoundOffSetting(models.TransientModel):
    _inherit = 'account.config.settings'

    discount_account = fields.Many2one('account.account', string='Discount Account')
    round_off_account_income = fields.Many2one('account.account', string='Round Off Account Income')
    round_off_account_expense = fields.Many2one('account.account', string='Round Off Account Expense')
    freight_account = fields.Many2one('account.account', string='Freight Account')
    union_account = fields.Many2one('account.account', string='Union Account')
    packing_account = fields.Many2one('account.account', string='Packing Account')
    other_account = fields.Many2one('account.account', string='Other Account')

    @api.multi
    def set_round_off(self):
        ir_values_obj = self.env['ir.values']

        ir_values_obj.sudo().set_default('account.config.settings', "discount_account", self.discount_account.id)
        ir_values_obj.sudo().set_default('account.config.settings', "round_off_account_income", self.round_off_account_income.id)
        ir_values_obj.sudo().set_default('account.config.settings', "round_off_account_expense", self.round_off_account_expense.id)
        ir_values_obj.sudo().set_default('account.config.settings', "freight_account", self.freight_account.id)
        ir_values_obj.sudo().set_default('account.config.settings', "union_account", self.union_account.id)
        ir_values_obj.sudo().set_default('account.config.settings', "packing_account", self.packing_account.id)
        ir_values_obj.sudo().set_default('account.config.settings', "other_account", self.other_account.id)