# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class pos_config(models.Model):
    _inherit = "pos.config"

    bus_id = fields.Many2one('pos.bus', string='Shop/bus location')

    user_ids = fields.Many2many('res.users', string='Assigned users')
