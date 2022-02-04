# -*- coding: utf-8 -*-
from odoo import http

# class PriceChangeCategory(http.Controller):
#     @http.route('/price_change_category/price_change_category/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/price_change_category/price_change_category/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('price_change_category.listing', {
#             'root': '/price_change_category/price_change_category',
#             'objects': http.request.env['price_change_category.price_change_category'].search([]),
#         })

#     @http.route('/price_change_category/price_change_category/objects/<model("price_change_category.price_change_category"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('price_change_category.object', {
#             'object': obj
#         })