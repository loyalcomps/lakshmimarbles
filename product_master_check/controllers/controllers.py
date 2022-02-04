# -*- coding: utf-8 -*-
from odoo import http

# class ProductMasterCheck(http.Controller):
#     @http.route('/product_master_check/product_master_check/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_master_check/product_master_check/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_master_check.listing', {
#             'root': '/product_master_check/product_master_check',
#             'objects': http.request.env['product_master_check.product_master_check'].search([]),
#         })

#     @http.route('/product_master_check/product_master_check/objects/<model("product_master_check.product_master_check"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_master_check.object', {
#             'object': obj
#         })