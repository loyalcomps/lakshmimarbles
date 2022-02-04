# -*- coding: utf-8 -*-
from odoo import http

# class RetailPriceUpdate(http.Controller):
#     @http.route('/retail_price_update/retail_price_update/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/retail_price_update/retail_price_update/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('retail_price_update.listing', {
#             'root': '/retail_price_update/retail_price_update',
#             'objects': http.request.env['retail_price_update.retail_price_update'].search([]),
#         })

#     @http.route('/retail_price_update/retail_price_update/objects/<model("retail_price_update.retail_price_update"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('retail_price_update.object', {
#             'object': obj
#         })