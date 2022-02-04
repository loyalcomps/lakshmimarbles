# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseBarcodeScan(http.Controller):
#     @http.route('/purchase_barcode_scan/purchase_barcode_scan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_barcode_scan/purchase_barcode_scan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_barcode_scan.listing', {
#             'root': '/purchase_barcode_scan/purchase_barcode_scan',
#             'objects': http.request.env['purchase_barcode_scan.purchase_barcode_scan'].search([]),
#         })

#     @http.route('/purchase_barcode_scan/purchase_barcode_scan/objects/<model("purchase_barcode_scan.purchase_barcode_scan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_barcode_scan.object', {
#             'object': obj
#         })