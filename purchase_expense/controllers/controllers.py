# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseExpense(http.Controller):
#     @http.route('/purchase_expense/purchase_expense/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_expense/purchase_expense/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_expense.listing', {
#             'root': '/purchase_expense/purchase_expense',
#             'objects': http.request.env['purchase_expense.purchase_expense'].search([]),
#         })

#     @http.route('/purchase_expense/purchase_expense/objects/<model("purchase_expense.purchase_expense"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_expense.object', {
#             'object': obj
#         })