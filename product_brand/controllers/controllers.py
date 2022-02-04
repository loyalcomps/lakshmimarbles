# -*- coding: utf-8 -*-
from odoo import http

# class ProductBrand(http.Controller):
#     @http.route('/product_brand/product_brand/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_brand/product_brand/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_brand.listing', {
#             'root': '/product_brand/product_brand',
#             'objects': http.request.env['product_brand.product_brand'].search([]),
#         })

#     @http.route('/product_brand/product_brand/objects/<model("product_brand.product_brand"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_brand.object', {
#             'object': obj
#         })