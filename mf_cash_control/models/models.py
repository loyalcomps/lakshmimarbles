# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    pos_session_id = fields.Many2one('pos.session', string="POS Session",store=True)
