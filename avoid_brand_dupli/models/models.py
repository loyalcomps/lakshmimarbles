# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class ProductBrand(models.Model):
    _inherit = 'product.brand'

    @api.model
    def create(self,vals):

        if 'name' in vals:
            exis_data_id = self.search([('name', '=ilike', vals['name'])])
            if exis_data_id:
                raise UserError(
                    _('Name already exist'))

        result = super(ProductBrand, self).create(vals)
        return result

    @api.multi
    def write(self, vals):

        if 'name' in vals:
            exis_data_id = self.search([('name', '=ilike', vals['name'])])
            if exis_data_id:
                raise UserError(
                    _('Name already exist'))

        result = super(ProductBrand, self).write(vals)
        return result

