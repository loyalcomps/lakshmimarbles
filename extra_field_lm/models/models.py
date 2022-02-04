# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name = 'product.template'

    product_mrp = fields.Float(string="MRP",default=0,digits=dp.get_precision('Product Price'))