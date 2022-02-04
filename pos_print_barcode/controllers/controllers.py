# -*- coding: utf-8 -*-
from odoo import http

# class PosPrintBarcode(http.Controller):
#     @http.route('/pos_print_barcode/pos_print_barcode/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_print_barcode/pos_print_barcode/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_print_barcode.listing', {
#             'root': '/pos_print_barcode/pos_print_barcode',
#             'objects': http.request.env['pos_print_barcode.pos_print_barcode'].search([]),
#         })

#     @http.route('/pos_print_barcode/pos_print_barcode/objects/<model("pos_print_barcode.pos_print_barcode"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_print_barcode.object', {
#             'object': obj
#         })