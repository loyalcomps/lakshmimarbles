# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class RoundOffSetting(models.TransientModel):
    _inherit = 'account.config.settings'

    sale_discount_account = fields.Many2one('account.account', string='Sale Discount Account', related='company_id.sale_discount_account')
    purchase_discount_account = fields.Many2one('account.account', string='Purchase Discount Account', related='company_id.purchase_discount_account')


    @api.multi
    def set_round_off(self):
        ir_values_obj = self.env['ir.values']

        ir_values_obj.sudo().set_default('account.config.settings', "sale_discount_account", self.sale_discount_account.id, for_all_users=True, company_id=self.company_id.id)
        ir_values_obj.sudo().set_default('account.config.settings', "purchase_discount_account", self.purchase_discount_account.id, for_all_users=True, company_id=self.company_id.id)

    @api.onchange('company_id')
    def onchange_company_id(self):
        res = super(RoundOffSetting, self).onchange_company_id()
        if self.company_id:
            self.sale_discount_account = self.company_id.sale_discount_account
            self.purchase_discount_account = self.company_id.purchase_discount_account

            # update accounts
            ir_values = self.env['ir.values']

            sale_discount_id = ir_values.get_default('account.config.settings', 'sale_discount_account',
                                                company_id=self.company_id.id)
            purchase_discount_id = ir_values.get_default('account.config.settings', 'purchase_discount_account',
                                               company_id=self.company_id.id)


            self.sale_discount_account = isinstance(sale_discount_id, list) and len(sale_discount_id) > 0 and sale_discount_id[
                0] or sale_discount_id
            self.purchase_discount_account = isinstance(purchase_discount_id, list) and len(purchase_discount_id) > 0 and purchase_discount_id[
                0] or purchase_discount_id

        return res


    @api.multi
    def set_salediscount_account(self):
        if self.sale_discount_account and self.sale_discount_account != self.company_id.sale_discount_account:
            self.company_id.write({'sale_discount_account': self.sale_discount_account.id})

    @api.multi
    def set_purchasediscount_account(self):
        if self.purchase_discount_account and self.purchase_discount_account != self.company_id.purchase_discount_account:
            self.company_id.write({'purchase_discount_account': self.purchase_discount_account.id})
