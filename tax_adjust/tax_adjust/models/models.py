# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountTax(models.Model):
    _inherit = 'account.tax'

    adjust_amount = fields.Float(required=False, digits=(16, 4))

    cess_adjust_amount = fields.Float(required=False, digits=(16, 4))


    # def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
    #     res = super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity, product, partner)
    #     self.ensure_one()
    #     if self.amount_type == 'percent' and self.price_include:
    #         if self.cess_adjust_amount != 0.0:
    #             if self.adjust_amount == 0.0 and self.cess_adjust_amount == 0.0:
    #                 return base_amount - (base_amount / (1 + self.amount / 100))
    #             else:
    #                 return (base_amount - (base_amount / (1 + self.adjust_amount / 100))) / self.cess_adjust_amount
    #
    #         else:
    #             if self.adjust_amount == 0.0:
    #                 return base_amount - (base_amount / (1 + self.amount / 100))
    #             else:
    #                 return (base_amount - (base_amount / (1 + self.adjust_amount / 100))) / 2
    #
    #
    #
    #
    #     return res


        # return super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity, product, partner)



