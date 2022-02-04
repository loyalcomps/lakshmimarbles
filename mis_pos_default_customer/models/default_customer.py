# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _

class PosConfig(models.Model):
    _inherit = 'pos.config' 

    default_customer_id = fields.Many2one('res.partner','Default Customer', domain=[('customer','=',True)])


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
