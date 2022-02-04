# -*- coding: utf-8 -*-
from odoo import http

# class ShelfBarcodePrint(http.Controller):
#     @http.route('/shelf_barcode_print/shelf_barcode_print/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shelf_barcode_print/shelf_barcode_print/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('shelf_barcode_print.listing', {
#             'root': '/shelf_barcode_print/shelf_barcode_print',
#             'objects': http.request.env['shelf_barcode_print.shelf_barcode_print'].search([]),
#         })

#     @http.route('/shelf_barcode_print/shelf_barcode_print/objects/<model("shelf_barcode_print.shelf_barcode_print"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shelf_barcode_print.object', {
#             'object': obj
#         })