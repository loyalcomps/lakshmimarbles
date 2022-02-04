# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import models, fields, api
from odoo import exceptions, _
from odoo.exceptions import UserError, ValidationError
import operator

class Alphonsa_unique_gst(models.Model):
    _inherit = 'purchase.order'

    @api.one
    @api.constrains('partner_ref')
    def _check_unique_ref(self):
        for line in self:
            if line.partner_ref:
                if len(self.search([('partner_ref', '=', line.partner_ref)])) > 1:
                    raise ValidationError("Reference Already Exists")
            else:
                pass

class Alphonsa_purchase_gst(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.constrains('reference')
    def _check_unique_ref(self):
        for line in self:
            if line.reference and line.type=='in_invoice':
                if len(self.search([('reference', '=', line.reference)])) > 1:
                    raise ValidationError("Reference Already Exists")
            else:
                pass

