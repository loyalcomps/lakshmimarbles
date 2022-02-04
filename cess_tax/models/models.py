# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    cess_id = fields.Many2one('account.tax', string='Customer Cess Rate',
                                domain=[('type_tax_use', '=', 'sale'),('cess', '=', True) ],related='product_tmpl_id.cess_id')

    supplier_cess_id = fields.Many2one('account.tax', string='Vendor Cess Rate',
                              domain=[('type_tax_use', '=', 'purchase'),('cess', '=', True)], related='product_tmpl_id.supplier_cess_id')

class ProductProduct(models.Model):
    _inherit = "product.template"

    cess_id = fields.Many2one('account.tax', string='Customer Cess Rate',
                                domain=[('type_tax_use', '=', 'sale'),('cess', '=', True)])
    supplier_cess_id = fields.Many2one('account.tax', string='Vendor Cess Rate',
                              domain=[('type_tax_use', '=', 'purchase'),('cess', '=', True)])



