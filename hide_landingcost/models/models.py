# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class user_landingcost(models.Model):
#     _name = 'user_landingcost.user_landingcost'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100