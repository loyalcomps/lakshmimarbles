# -*- coding: utf-8 -*-

import math

from odoo import models, fields, api,_
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from Number2Words import Number2Words

import odoo.addons.decimal_precision as dp

class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    def _get_amount(self, amt):

        amt = amt
        amount_in_word = Number2Words().convertNumberToWords(amt)
        return amount_in_word

class StockInherit(models.Model):
    _inherit = 'stock.picking'



    def _get_amount(self, amt):
        amt = amt
        amount_in_word = Number2Words().convertNumberToWords(amt)
        return amount_in_word

