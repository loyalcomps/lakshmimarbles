# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class ProductProduct(models.Model):
    _inherit = "product.product"

    min_sale_amt = fields.Float(string='Affordable Price',default=0,digits=dp.get_precision('Product Price'))

    @api.onchange('lst_price','min_sale_amt')
    def _check_min_sale_amt(self):
        if self.min_sale_amt>self.lst_price:
            raise ValidationError(_('Error ! Sale price is less than Affordable Price.'))
        # return True


# @api.constrains('min_sale_amt','lst_price')
    # def _check_min_sale_amt(self):
    #     if self.min_sale_amt>self.lst_price:
    #         raise ValidationError(_('Error ! Sale price is less than Affordable Price.'))
    #     return True

class ProductTemplate(models.Model):
    _inherit = "product.template"

    min_sale_amt = fields.Float('Affordable Price',related='product_variant_ids.min_sale_amt')

    @api.onchange('list_price', 'min_sale_amt')
    def _check_min_sale_amt(self):
        if self.min_sale_amt > self.list_price:
            raise ValidationError(_('Error ! Sale price is less than Affordable Price.'))

