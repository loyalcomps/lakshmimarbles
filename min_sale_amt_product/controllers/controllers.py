# -*- coding: utf-8 -*-
from odoo import http

# class MinSaleAmtProduct(http.Controller):
#     @http.route('/min_sale_amt_product/min_sale_amt_product/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/min_sale_amt_product/min_sale_amt_product/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('min_sale_amt_product.listing', {
#             'root': '/min_sale_amt_product/min_sale_amt_product',
#             'objects': http.request.env['min_sale_amt_product.min_sale_amt_product'].search([]),
#         })

#     @http.route('/min_sale_amt_product/min_sale_amt_product/objects/<model("min_sale_amt_product.min_sale_amt_product"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('min_sale_amt_product.object', {
#             'object': obj
#         })