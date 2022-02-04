# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError


class ProductBrand(models.Model):
    _name = "product.brand"

    name = fields.Char(string="Brand",required=True)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env['res.company']._company_default_get('product.brand'))

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name = 'product.template'

    brand_id = fields.Many2one('product.brand', string="Brand", related='product_variant_ids.brand_id')
    date_exp = fields.Date(string="Expiry Date", related='product_variant_ids.date_exp')
    product_mrp = fields.Float(string="MRP", related='product_variant_ids.product_mrp')
    type = fields.Selection([('product', 'Stockable Product'), ('consu', 'Consumable'), ('service', 'Service')],
                            'Product Type', required=True, default='product',
                            help="Consumable are product where you don't manage stock, a service is a non-material product provided by a company or an individual.")

    landing_cost = fields.Float(string="Landing Cost")

    @api.model
    def create(self, vals):

        product_template_id = super(ProductTemplate, self).create(vals)

        related_vals = {}
        if vals.get('brand_id'):
            related_vals['brand_id'] = vals['brand_id']
        if vals.get('product_mrp'):
            related_vals['product_mrp'] = vals['product_mrp']

        if vals.get('date_exp'):
            related_vals['date_exp'] = vals['date_exp']

        if related_vals:
            product_template_id.write(related_vals)

        return product_template_id

    @api.onchange('name')
    def onchange_product_name(self):

        count = 0

        if self.name:

            count = self.env['product.template'].search_count([('name', '=', self.name)])
            if count != 0:
                raise ValidationError(('Product Name Already Exist .'))


class ProductProduct(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('product.brand', string="Brand")
    date_exp = fields.Date(string="Expiry Date")
    product_mrp = fields.Float(string="MRP", )

    @api.onchange('name')
    def onchange_product_name(self):

        count = 0

        if self.name:

            count = self.env['product.product'].search_count([('name', '=', self.name)])
            if count != 0:
                raise ValidationError(('Product Name Already Exist .'))

    # @api.onchange('name')
    # def onchange_product_name(self):
    #
    #     count = 0
    #
    #     if self.name:
    #
    #         count = self.env['product.template'].search_count([('name', '=', self.name)])
    #         if count != 0:
    #             raise ValidationError(('Product Name Already Exist .'))



    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        # count = 0
        #
        # if vals.get('name'):
        #
        #     count = self.env['product.product'].search_count([('name', '=', vals['name'])])
        #     if count != 0:
        #         raise ValidationError(('Product Name Already Exist .'))

        if not vals.get('barcode'):
            res['barcode'] = self.env['ir.sequence'].next_by_code('product.barcode')

        return res


