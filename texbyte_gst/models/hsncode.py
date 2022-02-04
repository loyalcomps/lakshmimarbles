# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, fields, api
from odoo.osv import expression

#import logging
#log = logging.getLogger(__name__)

''' HSN (Harmonized Serial Number)Code (for India GST)'''
class HSN_Code(models.Model):
    _name = 'texbyte_gst.hsncode'
    _order = 'hsncode asc'

    hsncode = fields.Char(required=True,size=8,string="HSN Code")
    name = fields.Char(required=True,translate=True,string="Description")

    gst_tax_ids = fields.Many2many('account.tax', 'hsn_gst_taxes_rel', 'hsn_id', 'tax_id', string="GST Taxes", domain=[("active","=",True)])

    _sql_constraints = [ ('hsncode_uniq','unique(hsncode)','HSN code must be unique!') ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('hsncode', operator, name), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        hsncodes = self.search(domain + args, limit=limit)
        return hsncodes.name_get()


    @api.multi
    @api.depends('name', 'hsncode')
    def name_get(self):
        result = []
        for hsncode in self:
            name = hsncode.hsncode + ' ' + hsncode.name
            result.append((hsncode.id, name))
        return result


''' Place of Supply (Location/State) code '''
class GST_POS(models.Model):
    _name = 'texbyte_gst.gstpos'
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

