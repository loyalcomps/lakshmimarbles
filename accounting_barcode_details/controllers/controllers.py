# -*- coding: utf-8 -*-
from odoo import http

# class AccountingBarcodeDetails(http.Controller):
#     @http.route('/accounting_barcode_details/accounting_barcode_details/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/accounting_barcode_details/accounting_barcode_details/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('accounting_barcode_details.listing', {
#             'root': '/accounting_barcode_details/accounting_barcode_details',
#             'objects': http.request.env['accounting_barcode_details.accounting_barcode_details'].search([]),
#         })

#     @http.route('/accounting_barcode_details/accounting_barcode_details/objects/<model("accounting_barcode_details.accounting_barcode_details"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('accounting_barcode_details.object', {
#             'object': obj
#         })