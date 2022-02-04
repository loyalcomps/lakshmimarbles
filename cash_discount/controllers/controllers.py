# -*- coding: utf-8 -*-
from openerp import http

# class CashDiscount(http.Controller):
#     @http.route('/cash_discount/cash_discount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cash_discount/cash_discount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cash_discount.listing', {
#             'root': '/cash_discount/cash_discount',
#             'objects': http.request.env['cash_discount.cash_discount'].search([]),
#         })

#     @http.route('/cash_discount/cash_discount/objects/<model("cash_discount.cash_discount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cash_discount.object', {
#             'object': obj
#         })