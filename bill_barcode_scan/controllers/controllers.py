# -*- coding: utf-8 -*-
from odoo import http

# class BillBarcodeScan(http.Controller):
#     @http.route('/bill_barcode_scan/bill_barcode_scan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bill_barcode_scan/bill_barcode_scan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bill_barcode_scan.listing', {
#             'root': '/bill_barcode_scan/bill_barcode_scan',
#             'objects': http.request.env['bill_barcode_scan.bill_barcode_scan'].search([]),
#         })

#     @http.route('/bill_barcode_scan/bill_barcode_scan/objects/<model("bill_barcode_scan.bill_barcode_scan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bill_barcode_scan.object', {
#             'object': obj
#         })