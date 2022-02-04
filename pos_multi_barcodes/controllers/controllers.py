# -*- coding: utf-8 -*-
from odoo import http

# class PosMultiBarcodes(http.Controller):
#     @http.route('/pos_multi_barcodes/pos_multi_barcodes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_multi_barcodes/pos_multi_barcodes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_multi_barcodes.listing', {
#             'root': '/pos_multi_barcodes/pos_multi_barcodes',
#             'objects': http.request.env['pos_multi_barcodes.pos_multi_barcodes'].search([]),
#         })

#     @http.route('/pos_multi_barcodes/pos_multi_barcodes/objects/<model("pos_multi_barcodes.pos_multi_barcodes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_multi_barcodes.object', {
#             'object': obj
#         })