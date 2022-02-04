# -*- coding: utf-8 -*-

from odoo import models, fields, api

class loyal_pos_userrights(models.Model):
    _inherit = 'res.users'

    pos_configuser = fields.Many2one('pos.config', 'Default Point of Sale')







#     _name = 'loyal_pos_userrights.loyal_pos_userrights'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100