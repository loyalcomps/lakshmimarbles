# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class PurchaseExpenseAccount(models.TransientModel):
    _inherit = 'account.config.settings'

    # freight_account = fields.Many2one('account.account', string='Freight Account')
    freight_account_purchase = fields.Many2one('account.account', string='Freight Account(Purchase)')
    union_account = fields.Many2one('account.account', string='Union Account')
    packing_account = fields.Many2one('account.account', string='Packing Account')
    other_account = fields.Many2one('account.account', string='Other Account')

    @api.multi
    def set_purchase_expense_account(self):
        ir_values_obj = self.env['ir.values']

        ir_values_obj.sudo().set_default('account.config.settings', "freight_account_purchase", self.freight_account_purchase.id)
        ir_values_obj.sudo().set_default('account.config.settings', "union_account", self.union_account.id)
        ir_values_obj.sudo().set_default('account.config.settings', "packing_account", self.packing_account.id)
        ir_values_obj.sudo().set_default('account.config.settings', "other_account", self.other_account.id)