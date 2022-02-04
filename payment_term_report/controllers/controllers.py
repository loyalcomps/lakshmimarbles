# -*- coding: utf-8 -*-
from odoo import http

# class PaymentTermReport(http.Controller):
#     @http.route('/payment_term_report/payment_term_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_term_report/payment_term_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_term_report.listing', {
#             'root': '/payment_term_report/payment_term_report',
#             'objects': http.request.env['payment_term_report.payment_term_report'].search([]),
#         })

#     @http.route('/payment_term_report/payment_term_report/objects/<model("payment_term_report.payment_term_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_term_report.object', {
#             'object': obj
#         })