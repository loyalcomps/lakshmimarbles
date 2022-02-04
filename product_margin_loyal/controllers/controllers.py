# -*- coding: utf-8 -*-
from odoo import http

# class ProductMargin(http.Controller):
#     @http.route('/product_margin/product_margin/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_margin/product_margin/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_margin.listing', {
#             'root': '/product_margin/product_margin',
#             'objects': http.request.env['product_margin.product_margin'].search([]),
#         })

#     @http.route('/product_margin/product_margin/objects/<model("product_margin.product_margin"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_margin.object', {
#             'object': obj
#         })