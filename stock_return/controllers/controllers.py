# -*- coding: utf-8 -*-
from odoo import http

# class StockReturn(http.Controller):
#     @http.route('/stock_return/stock_return/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_return/stock_return/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_return.listing', {
#             'root': '/stock_return/stock_return',
#             'objects': http.request.env['stock_return.stock_return'].search([]),
#         })

#     @http.route('/stock_return/stock_return/objects/<model("stock_return.stock_return"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_return.object', {
#             'object': obj
#         })