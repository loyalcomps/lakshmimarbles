# -*- coding: utf-8 -*-
from odoo import http

# class BarcodeNameSearch(http.Controller):
#     @http.route('/barcode_name_search/barcode_name_search/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/barcode_name_search/barcode_name_search/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('barcode_name_search.listing', {
#             'root': '/barcode_name_search/barcode_name_search',
#             'objects': http.request.env['barcode_name_search.barcode_name_search'].search([]),
#         })

#     @http.route('/barcode_name_search/barcode_name_search/objects/<model("barcode_name_search.barcode_name_search"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('barcode_name_search.object', {
#             'object': obj
#         })