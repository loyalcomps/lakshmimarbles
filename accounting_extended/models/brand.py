# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class ProductBrand(models.Model):
    _name = "product.brand"

    name = fields.Char(string="Brand",required=True)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self: self.env['res.company']._company_default_get('product.brand'))

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name = 'product.template'
    brand_id = fields.Many2one('product.brand', string="Brand", related='product_variant_ids.brand_id')
    product_mrp = fields.Float(string="MRP",default=0,digits=dp.get_precision('Product Price'))
    hsn = fields.Char(string="HSN/SAC")
    type = fields.Selection([('product', 'Stockable Product'), ('consu', 'Consumable'), ('service', 'Service')],
                            'Product Type', required=True, default='product',
                            help="Consumable are product where you don't manage stock, a service is a non-material product provided by a company or an individual.")

    expiry_date = fields.Date(string='Expiry date',help="Expiry date", copy=False)

    landing_cost = fields.Float(string="Landing Cost")
    @api.model
    def create(self, vals):

        product_template_id = super(ProductTemplate, self).create(vals)
        related_vals = {}
        if vals.get('brand_id'):
            related_vals['brand_id'] = vals['brand_id']
        if related_vals:
            product_template_id.write(related_vals)

        return product_template_id


class ProductProduct(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('product.brand', string="Brand")


    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        if not vals.get('barcode'):
            res['barcode'] = self.env['ir.sequence'].next_by_code('product.barcode')

        return res


