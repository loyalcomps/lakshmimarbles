# -*- coding: utf-8 -*-
from odoo import http

# class ProductHide(http.Controller):
#     @http.route('/product_hide/product_hide/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_hide/product_hide/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_hide.listing', {
#             'root': '/product_hide/product_hide',
#             'objects': http.request.env['product_hide.product_hide'].search([]),
#         })

#     @http.route('/product_hide/product_hide/objects/<model("product_hide.product_hide"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_hide.object', {
#             'object': obj
#         })