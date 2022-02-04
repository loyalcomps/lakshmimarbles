# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('prevent_partial_payment','property_payment_term_id')
    def _get_prevent_partial_payment(self):
        for obj in self:
            obj.prevent_partial_payment = obj.property_payment_term_id.prevent_partial_payment

    prevent_partial_payment = fields.Boolean(compute="_get_prevent_partial_payment", string="Don't allow partial payment in POS")