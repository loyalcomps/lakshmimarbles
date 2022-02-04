# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    used_for_rounding = fields.Boolean(string="Used For Rounding")
    visible_in_pos = fields.Boolean(string="Visible in pos")
    allow_rounding = fields.Boolean(string="Allow Automatic Rounding")
    decimal_rounding = fields.Integer(string = "Decimal Rounding")

