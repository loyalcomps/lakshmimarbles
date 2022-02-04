# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, fields, api
from odoo.osv import expression

#import logging
#log = logging.getLogger(__name__)

''' Place of Supply of the Company '''
class GST_Company(models.Model):
    _inherit = 'res.company'


    # Place of Supply for GST (default 32 - Kerala)
    place_of_supply = fields.Many2one('gstr3b_report.gstpos',
                                        string="Compnay's Place of Supply",
                                        default=lambda self: self.env['gstr3b_report.gstpos'].search([('name','ilike',self.state_id)],limit=1) if self.state_id else self.env['gstr3b_report.gstpos'].search([('poscode','=','32')],limit=1))


    @api.onchange('state_id')
    def _set_place_of_supply(self):
         if self.state_id:
             self.place_of_supply = self.env['gstr3b_report.gstpos'].search([('name','ilike',self.state_id.name)])
