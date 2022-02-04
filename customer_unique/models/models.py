# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Res_Partner(models.Model):
    _inherit = 'res.partner'

    is_loyalty = fields.Boolean('Loyality')

    _sql_constraints = [('barcode_uniq', 'unique (barcode)', "Barcode already exists !")]

    @api.model
    def create(self, vals):

        res = super(Res_Partner, self).create(vals)
        related_vals = {}
        if vals.get('customer'):
            if vals.get('customer') == True:
                if not vals.get('barcode'):
                    related_vals['barcode'] = self.env['ir.sequence'].next_by_code('loyalty.barcode')
        if related_vals:
            res.write(related_vals)

        return res

    @api.multi
    def write(self, vals):

        if vals.get('customer'):
            if vals.get('customer') == True:
                if not self.barcode:
                    self.barcode = self.env['ir.sequence'].next_by_code('loyalty.barcode')

        return super(Res_Partner, self).write(vals)