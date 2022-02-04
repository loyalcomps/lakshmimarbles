# -*- coding: utf-8 -*-

from odoo import models, fields, api

# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class pos_promotion(models.Model):
    _name = "pos.promotion"
    _description = "Management Promotion on pos"

    name = fields.Char('Name', required=1)
    active = fields.Boolean('Active', default=1)
    start_date = fields.Datetime('Start date', default=fields.Datetime.now(), required=1)
    end_date = fields.Datetime('End date', required=1)
    type = fields.Selection([
        # ('1_discount_total_order', '1. Discount each amount total order'),
        # ('2_discount_category', '2. Discount each category'),
        # ('3_discount_by_quantity_of_product', '3. Discount each quantity of product'),
        # ('4_pack_discount', '4. Buy pack products discount products'),
        ('5_pack_free_gift', '5. Buy pack products free products'),
        # ('6_price_filter_quantity', '6. Sale off products'),
        # ('7_special_category', '7. Discount each special category'),
        # ('8_discount_lowest_price', '8. Discount lowest price'),
        # ('9_multi_buy', '9. Multi buy - By X for price'),
        # ('10_buy_x_get_another_free', '10. Buy x get another free'),
    ], 'Type', default='5_pack_free_gift', required=1)
    product_id = fields.Many2one('product.product', 'Product service', domain=[('available_in_pos', '=', True)])

    gift_condition_ids = fields.One2many('pos.promotion.gift.condition', 'promotion_id', 'Gifts condition')
    gift_free_ids = fields.One2many('pos.promotion.gift.free', 'promotion_id', 'Gifts apply')



    config_ids = fields.Many2many('pos.config',
                                     'pos_config_promotion_rel',
                                     'promotion_id',
                                     'config_id',
                                     string='POS config')

    @api.model
    def default_get(self, fields):
        res = super(pos_promotion, self).default_get(fields)
        products = self.env['product.product'].search([('name', '=', 'Promotion service')])
        if products:
            res.update({'product_id': products[0].id})
        return res







class pos_promotion_gift_condition(models.Model):
    _name = "pos.promotion.gift.condition"
    _order = "product_id, minimum_quantity"
    _description = "Promotion gift condition"

    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product',
                                 required=1)
    minimum_quantity = fields.Float('Qty greater or equal', required=1, default=1.0)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_gift_free(models.Model):
    _name = "pos.promotion.gift.free"
    _order = "product_id"
    _description = "Promotion give gift to customer"

    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product gift',
                                 required=1)
    quantity_free = fields.Float('Quantity free', required=1, default=1.0)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1, ondelete='cascade')
