# -*- coding: utf-8 -*-
from odoo import http

# class UpdateSalePrice(http.Controller):
#     @http.route('/update_sale_price/update_sale_price/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/update_sale_price/update_sale_price/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('update_sale_price.listing', {
#             'root': '/update_sale_price/update_sale_price',
#             'objects': http.request.env['update_sale_price.update_sale_price'].search([]),
#         })

#     @http.route('/update_sale_price/update_sale_price/objects/<model("update_sale_price.update_sale_price"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('update_sale_price.object', {
#             'object': obj
#         })