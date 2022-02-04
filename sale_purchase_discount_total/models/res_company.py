# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class ResCompany(models.Model):
    _inherit = "res.company"

    sale_discount_account = fields.Many2one('account.account',
                                          domain=lambda self: [('user_type_id.id', '=',
                                                                                          self.env.ref(
                                                                                              'account.data_account_type_expenses').id),
                                                               ('deprecated', '=', False)],
                                          string="Sale Discount Account")
    purchase_discount_account = fields.Many2one('account.account',
                                            domain=lambda self: [('user_type_id.id', '=',
                                                                  self.env.ref(
                                                                      'account.data_account_type_revenue').id),
                                                                 ('deprecated', '=', False)],
                                            string="Purchase Discount Account")