# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, fields, api
from odoo.osv import expression

#import logging
#log = logging.getLogger(__name__)

''' Place of Supply of the Company '''
class GST_CountryState(models.Model):
    _inherit = 'res.country.state'

    # Some states in India are 'Union Territories', not 'States'. They have 'UTGST' applicable instead of 'SGST'
    union_territory = fields.Boolean(string="Union Territory")
