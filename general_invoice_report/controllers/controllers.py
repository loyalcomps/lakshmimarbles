# -*- coding: utf-8 -*-
from odoo import http

# class GeneralInvoiceReport(http.Controller):
#     @http.route('/general_invoice_report/general_invoice_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/general_invoice_report/general_invoice_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('general_invoice_report.listing', {
#             'root': '/general_invoice_report/general_invoice_report',
#             'objects': http.request.env['general_invoice_report.general_invoice_report'].search([]),
#         })

#     @http.route('/general_invoice_report/general_invoice_report/objects/<model("general_invoice_report.general_invoice_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('general_invoice_report.object', {
#             'object': obj
#         })