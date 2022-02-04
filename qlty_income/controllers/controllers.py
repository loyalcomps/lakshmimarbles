# -*- coding: utf-8 -*-
from odoo import http

# class AmsExpense(http.Controller):
#     @http.route('/ams_expense/ams_expense/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ams_expense/ams_expense/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ams_expense.listing', {
#             'root': '/ams_expense/ams_expense',
#             'objects': http.request.env['ams_expense.ams_expense'].search([]),
#         })

#     @http.route('/ams_expense/ams_expense/objects/<model("ams_expense.ams_expense"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ams_expense.object', {
#             'object': obj
#         })