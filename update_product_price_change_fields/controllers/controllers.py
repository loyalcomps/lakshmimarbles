# -*- coding: utf-8 -*-
from odoo import http

# class UpdateProductPriceChangeFields(http.Controller):
#     @http.route('/update_product_price_change_fields/update_product_price_change_fields/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/update_product_price_change_fields/update_product_price_change_fields/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('update_product_price_change_fields.listing', {
#             'root': '/update_product_price_change_fields/update_product_price_change_fields',
#             'objects': http.request.env['update_product_price_change_fields.update_product_price_change_fields'].search([]),
#         })

#     @http.route('/update_product_price_change_fields/update_product_price_change_fields/objects/<model("update_product_price_change_fields.update_product_price_change_fields"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('update_product_price_change_fields.object', {
#             'object': obj
#         })