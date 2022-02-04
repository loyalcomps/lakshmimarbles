# -*- coding: utf-8 -*-
from odoo import http

# class DebitCreditNote(http.Controller):
#     @http.route('/debit_credit_note/debit_credit_note/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/debit_credit_note/debit_credit_note/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('debit_credit_note.listing', {
#             'root': '/debit_credit_note/debit_credit_note',
#             'objects': http.request.env['debit_credit_note.debit_credit_note'].search([]),
#         })

#     @http.route('/debit_credit_note/debit_credit_note/objects/<model("debit_credit_note.debit_credit_note"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('debit_credit_note.object', {
#             'object': obj
#         })