# -*- coding: utf-8 -*-
from odoo import http

# class MultiBarcodeUom(http.Controller):
#     @http.route('/multi_barcode_uom/multi_barcode_uom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/multi_barcode_uom/multi_barcode_uom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('multi_barcode_uom.listing', {
#             'root': '/multi_barcode_uom/multi_barcode_uom',
#             'objects': http.request.env['multi_barcode_uom.multi_barcode_uom'].search([]),
#         })

#     @http.route('/multi_barcode_uom/multi_barcode_uom/objects/<model("multi_barcode_uom.multi_barcode_uom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('multi_barcode_uom.object', {
#             'object': obj
#         })