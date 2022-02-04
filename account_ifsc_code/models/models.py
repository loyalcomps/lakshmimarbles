# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_ifsc_code(models.Model):
    _inherit = 'res.partner.bank'

    ifsc_code = fields.Char('IFSC Code',store=True)
