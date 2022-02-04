# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PriceChangeCategory(models.TransientModel):
    _name = 'price.change.category'

    category_id = fields.Many2one('product.category',string='Category')
    sale_price = fields.Float(string='Sale Price',)
    min_sale_amt = fields.Float(string='Affordable Price', )
    price_change_line_ids = fields.One2many('price.change.line', 'price_change_id', string='Product Info')
    company_id = fields.Many2one('res.company', string='Company', store=True,
                                 readonly=True,default=lambda self: self.env.user.company_id.id)

    @api.constrains('min_sale_amt', 'sale_price')
    def _check_min_sale_amt(self):
        if self.min_sale_amt > self.sale_price:
            raise ValidationError(_('Error ! Sale price must be greater then Affordable Price.'))
        return True

    @api.onchange('category_id')
    def load_products(self):
        if not self.category_id:
            return
        self.sale_price = self.category_id.sale_price
        self.min_sale_amt = self.category_id.min_sale_amt
        category = self.env['product.category'].search([('id','child_of',self.category_id.id)])
        category_id = [x.id for x in category]
        # category_ids = tuple(category_id)
        pd_list = []


        query='''select pp.min_sale_amt,pt.list_price,pp.id from product_product pp
            left join product_template pt on pp.product_tmpl_id=pt.id
            where pt.categ_id in %s and pt.company_id=%s and pt.sale_ok = true and pt.active = true'''
        self.env.cr.execute(query,(tuple(category_id),self.company_id.id))
        for row in self.env.cr.dictfetchall():
            values = {
                'product_id':row['id'],
                'sale_price':row['list_price'],
                'min_sale_amt':row['min_sale_amt']
            }
            pd_list.append((0, 0, values))
        self.update({'price_change_line_ids': pd_list,
                     })

    @api.onchange('sale_price','category_id')
    def change_sale_price(self):
        for record in self:
            pd_list = []
            for line in record.price_change_line_ids:

                line.sale_price = record.sale_price

    @api.onchange('min_sale_amt', 'category_id')
    def change_minimum_price(self):
        for record in self:
            for line in record.price_change_line_ids:
                line.min_sale_amt = record.min_sale_amt


    @api.multi
    def update_price(self):
        for record in self:
            product_list = [line.product_id.name for line in record.price_change_line_ids if
                            line.sale_price < line.min_sale_amt]
            if product_list:
                if len(product_list) > 1:
                    message = _(
                        "The following products Price is less than the affordable price:") + '\n'
                    message += '\n'.join(map(str, product_list))

                else:
                    message = _(
                        "The following product Price is less than the affordable price:") + '\n'
                    message += '\n'.join(map(str, product_list))

                raise ValidationError(_(message))
            for line in record.price_change_line_ids:
                line.product_id.update ({
                    'min_sale_amt':line.min_sale_amt,
                    'lst_price':line.sale_price
                })
            record.category_id.update({
                'min_sale_amt': record.min_sale_amt,
                'sale_price': record.sale_price
            })

class PriceChangeCategoryLine(models.TransientModel):
    _name = 'price.change.line'

    price_change_id = fields.Many2one('price.change.category', string='Price ChangeReference',
                                 ondelete='cascade', index=True, required=True, copy=False)
    sale_price = fields.Float(string='Sale Price', )
    min_sale_amt = fields.Float(string='Affordable Price', )
    product_id = fields.Many2one('product.product',string='Product',domain=[('sale_ok','=',True),('active','=',True)])

    @api.onchange('product_id')
    def load_product_price(self):
        if not self.product_id:
            return
        self.update({
            'sale_price':self.product_id.lst_price,
            'min_sale_amt':self.product_id.min_sale_amt,
        })

    # @api.constrains('min_sale_amt', 'sale_price')
    # def _check_min_sale_amt(self):
    #     if self.min_sale_amt > self.sale_price:
    #         raise ValidationError(_('Error ! Sale price must be greater then Affordable Price.'))
    #     return True

