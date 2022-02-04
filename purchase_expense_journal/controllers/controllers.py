# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseExpenseJournal(http.Controller):
#     @http.route('/purchase_expense_journal/purchase_expense_journal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_expense_journal/purchase_expense_journal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_expense_journal.listing', {
#             'root': '/purchase_expense_journal/purchase_expense_journal',
#             'objects': http.request.env['purchase_expense_journal.purchase_expense_journal'].search([]),
#         })

#     @http.route('/purchase_expense_journal/purchase_expense_journal/objects/<model("purchase_expense_journal.purchase_expense_journal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_expense_journal.object', {
#             'object': obj
#         })