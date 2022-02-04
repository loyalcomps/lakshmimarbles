# -*- coding: utf-8 -*-
from odoo import http

# class GrandBarcodeColor(http.Controller):
#     @http.route('/grand_barcode_color/grand_barcode_color/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/grand_barcode_color/grand_barcode_color/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('grand_barcode_color.listing', {
#             'root': '/grand_barcode_color/grand_barcode_color',
#             'objects': http.request.env['grand_barcode_color.grand_barcode_color'].search([]),
#         })

#     @http.route('/grand_barcode_color/grand_barcode_color/objects/<model("grand_barcode_color.grand_barcode_color"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('grand_barcode_color.object', {
#             'object': obj
#         })