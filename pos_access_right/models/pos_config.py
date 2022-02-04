# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    cash_discount = fields.Boolean('Allow cash discount', default=True)
    pos_discount = fields.Boolean('Allow POS discount', default=True)
    allow_discount = fields.Boolean('Allow discount', default=True)
    allow_edit_price = fields.Boolean('Allow edit price', default=True)

