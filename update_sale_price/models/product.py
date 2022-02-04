# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'

    margin_discount_perc = fields.Float(string='Margin Discount%',default=0)

    margin_discount = fields.Float(string='Margin Discount',default=0)

    @api.depends('categ_id')
    def change_sell_price(self):
        self.margin_discount_perc = self.categ_id.margin_discount_perc
        self.margin_discount = self.categ_id.margin_discount
        if self.margin:
            if self.margin_discount_perc:
                self.lst_price = self.product_mrp - (self.margin*self.margin_discount_perc/100)
            elif self.margin_discount:
                self.lst_price = self.product_mrp - (self.margin_discount)




class Product(models.Model):
    _inherit = 'product.product'

    @api.onchange('categ_id','margin')
    def change_sell_price(self):
        self.margin_discount_perc = self.categ_id.margin_discount_perc
        self.margin_discount = self.categ_id.margin_discount
        if self.margin:
            if self.margin_discount_perc:
                self.lst_price = self.product_mrp - (self.margin*self.margin_discount_perc/100)
            elif self.margin_discount:
                self.lst_price = self.product_mrp - (self.margin_discount)




