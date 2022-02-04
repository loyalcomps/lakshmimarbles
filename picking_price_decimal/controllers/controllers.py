# -*- coding: utf-8 -*-
from odoo import http

# class PickingPriceDecimal(http.Controller):
#     @http.route('/picking_price_decimal/picking_price_decimal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/picking_price_decimal/picking_price_decimal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('picking_price_decimal.listing', {
#             'root': '/picking_price_decimal/picking_price_decimal',
#             'objects': http.request.env['picking_price_decimal.picking_price_decimal'].search([]),
#         })

#     @http.route('/picking_price_decimal/picking_price_decimal/objects/<model("picking_price_decimal.picking_price_decimal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('picking_price_decimal.object', {
#             'object': obj
#         })