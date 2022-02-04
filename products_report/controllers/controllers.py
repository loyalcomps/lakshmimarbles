# -*- coding: utf-8 -*-
from odoo import http

# class ProductsReport(http.Controller):
#     @http.route('/products_report/products_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/products_report/products_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('products_report.listing', {
#             'root': '/products_report/products_report',
#             'objects': http.request.env['products_report.products_report'].search([]),
#         })

#     @http.route('/products_report/products_report/objects/<model("products_report.products_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('products_report.object', {
#             'object': obj
#         })