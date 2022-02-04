# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class IrActionsActWindow_Extend(models.Model):
    _inherit = 'ir.actions.act_window'

    auto_refresh = fields.Integer('Auto Refresh')
