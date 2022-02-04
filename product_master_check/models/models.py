# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
import logging
from odoo.models import BaseModel

_logger = logging.getLogger(__name__)







class purchsase_order(models.Model):
    _inherit = 'purchase.order.line'


    @api.multi
    def write(self,values):


        for line in self:
            if line.is_check == False:
                if line.product_mrp < line.sale_price:
                    pass
            if line.is_check == True:
                if 'sale_price' in values and 'product_mrp' not in values:

                    if line.product_mrp < values['sale_price']:
                        raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
                elif 'sale_price' not in values and 'product_mrp' in values:
                    if values['product_mrp'] < line.sale_price:
                        raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
                elif 'sale_price' in values and 'product_mrp' in values:
                    if values['product_mrp'] < values['sale_price']:
                        raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
                else:
                    if line.product_mrp < line.sale_price:
                        raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)

        return super(purchsase_order, self).write(values)

class Account_invoice(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def write(self,values):

        for line in self:
            if line.is_check == False:
                if line.product_mrp < line.sale_price:
                    pass
            if line.is_check == True:
                if 'sale_price' in values and 'product_mrp' not in values:

                    if line.product_mrp < values['sale_price']:
                        raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
                elif 'sale_price' not in values and 'product_mrp' in values:
                    if values['product_mrp'] < line.sale_price:
                        raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
                elif 'sale_price' in values and 'product_mrp' in values:
                    if values['product_mrp'] < values['sale_price']:
                        raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
                else:
                    if line.product_mrp < line.sale_price:
                        raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)

        return super(Account_invoice, self).write(values)




class product_barcode_check(models.Model):
    _inherit = 'product.barcode'



    @api.multi
    @api.constrains('product_mrp','list_price')
    def _check_mrp_landing_sale_price(self):

        for line in self:

            if line.product_mrp < line.list_price:
                raise ValidationError(_("Cannot Give Sale Price Greater Than MRP "))

class ProductProduct(models.Model):
    _inherit = 'product.product'


    @api.multi
    def write(self, values):


        ''' Store the standard price change in order to be able to retrieve the cost of a product for a given date'''
        if 'lst_price' in values and 'product_mrp' not in values:
            product_id = self.env['purchase.order.line'].search([('product_id', '=', self.id)])
            purchase = self.env['purchase.order.line']
            invproduct_id = self.env['account.invoice.line'].search([('product_id', '=', self.id)])
            inv = self.env['account.invoice.line']
            p_id = self.env['purchase.order.line'].search([('product_mrp', '=', self.product_mrp)])

            # if product_id:
            #     for line in purchase:
            #         if line.is_check == False:
            #             if line.product_mrp < line.sale_price:
            #                 pass
            #         if line.is_check == True:
            #             if 'sale_price' in values and 'product_mrp' not in values:
            #
            #                 if line.product_mrp < values['sale_price']:
            #                     raise ValidationError(
            #                         _("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
            #             elif 'sale_price' not in values and 'product_mrp' in values:
            #                 if values['product_mrp'] < line.sale_price:
            #                     raise ValidationError(
            #                         _("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
            #             elif 'sale_price' in values and 'product_mrp' in values:
            #                 if values['product_mrp'] < values['sale_price']:
            #                     raise ValidationError(
            #                         _("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
            #             else:
            #                 if line.product_mrp < line.sale_price:
            #                     raise ValidationError(
            #                         _("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
            # elif invproduct_id:
            #     for i in inv:
            #         self.product_mrp = i.product_mrp
            #         if i.product_mrp < values['lst_price']:
            #             raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
            #
            # # if product_id:
            # #     return super(purchsase_order, self).write(values)
            # # elif invproduct_id:
            # #     return super(Account_invoice, self).write(values)
            #
            # else:

            if self.product_mrp < values['lst_price']:
                raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
        elif 'lst_price' not in values and 'product_mrp' in values:
            if values['product_mrp'] < self.lst_price:
                raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
        elif 'lst_price' in values and 'product_mrp' in values:
            if values['product_mrp'] < values['lst_price']:
                raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)
        else:
            if self.product_mrp < self.lst_price:
                raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % self.name)



        return super(ProductProduct, self).write(values)





