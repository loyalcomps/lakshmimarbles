# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        if res['to_weight'] == True:
            if not vals.get('plu'):
                res['plu'] = self.env['ir.sequence'].next_by_code('product.product')

        return res

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if res['to_weight'] == True:
            if not vals.get('plu'):
                res['plu'] = self.env['ir.sequence'].next_by_code('product.template')

        return res