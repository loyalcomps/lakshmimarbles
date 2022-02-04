# -*- coding: utf-8 -*-
from odoo import http

# class ProductsLabelsExtend(http.Controller):
#     @http.route('/products_labels_extend/products_labels_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/products_labels_extend/products_labels_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('products_labels_extend.listing', {
#             'root': '/products_labels_extend/products_labels_extend',
#             'objects': http.request.env['products_labels_extend.products_labels_extend'].search([]),
#         })

#     @http.route('/products_labels_extend/products_labels_extend/objects/<model("products_labels_extend.products_labels_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('products_labels_extend.object', {
#             'object': obj
#         })