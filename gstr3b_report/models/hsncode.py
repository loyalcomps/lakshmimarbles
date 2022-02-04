# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, fields, api
from odoo.osv import expression

#import logging
#log = logging.getLogger(__name__)



''' Place of Supply (Location/State) code '''
class GST_POS(models.Model):
    _name = 'gstr3b_report.gstpos'
    _order = 'poscode asc'
    _rec_name = 'state_id'

    poscode = fields.Char(required=True,size=2,string="Code")
    state_id = fields.Many2one('res.country.state',required=True,string="Place of Supply")


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('poscode', '=ilike', name + '%'), ('state_id.name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        poscodes = self.search(domain + args, limit=limit)
        return poscodes.name_get()


    @api.multi
    @api.depends('state_id', 'poscode')
    def name_get(self):
        result = []
        for poscode in self:
            name = poscode.poscode + '-' + poscode.state_id.name
            result.append((poscode.id, name))
        return result

