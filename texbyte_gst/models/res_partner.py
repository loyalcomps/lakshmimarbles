# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, fields, api
from odoo.exceptions import ValidationError

#import logging
#log = logging.getLogger(__name__)

class GST_Partner(models.Model):
    _inherit = 'res.partner'

    "Do not allow duplicated GST (VAT) numbers"
    @api.one
    @api.constrains('vat')
    def check_duplicate_gst_number(self):
        if self.vat and self.env['res.partner'].search_count([('vat', '=', self.vat),('parent_id', '=', False)]) > 1:
            raise ValidationError("Party with this GST number already exists.\nYou meant to add Invoice/Shipping address?")

