# -*- coding: utf-8 -*-
from odoo import http

# class ProductSalePrice(http.Controller):
#     @http.route('/product_sale_price/product_sale_price/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_sale_price/product_sale_price/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_sale_price.listing', {
#             'root': '/product_sale_price/product_sale_price',
#             'objects': http.request.env['product_sale_price.product_sale_price'].search([]),
#         })

#     @http.route('/product_sale_price/product_sale_price/objects/<model("product_sale_price.product_sale_price"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_sale_price.object', {
#             'object': obj
#         })