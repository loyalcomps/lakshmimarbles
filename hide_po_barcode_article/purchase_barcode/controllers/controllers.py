# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseBarcode(http.Controller):
#     @http.route('/purchase_barcode/purchase_barcode/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_barcode/purchase_barcode/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_barcode.listing', {
#             'root': '/purchase_barcode/purchase_barcode',
#             'objects': http.request.env['purchase_barcode.purchase_barcode'].search([]),
#         })

#     @http.route('/purchase_barcode/purchase_barcode/objects/<model("purchase_barcode.purchase_barcode"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_barcode.object', {
#             'object': obj
#         })