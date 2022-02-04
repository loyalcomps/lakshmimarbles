# -*- coding: utf-8 -*-
from odoo import http

# class ChequePaymentPrint(http.Controller):
#     @http.route('/cheque_payment_print/cheque_payment_print/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cheque_payment_print/cheque_payment_print/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cheque_payment_print.listing', {
#             'root': '/cheque_payment_print/cheque_payment_print',
#             'objects': http.request.env['cheque_payment_print.cheque_payment_print'].search([]),
#         })

#     @http.route('/cheque_payment_print/cheque_payment_print/objects/<model("cheque_payment_print.cheque_payment_print"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cheque_payment_print.object', {
#             'object': obj
#         })