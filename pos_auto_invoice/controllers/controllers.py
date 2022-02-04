# -*- coding: utf-8 -*-
from odoo import http

# class PosAutoInvoice(http.Controller):
#     @http.route('/pos_auto_invoice/pos_auto_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_auto_invoice/pos_auto_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_auto_invoice.listing', {
#             'root': '/pos_auto_invoice/pos_auto_invoice',
#             'objects': http.request.env['pos_auto_invoice.pos_auto_invoice'].search([]),
#         })

#     @http.route('/pos_auto_invoice/pos_auto_invoice/objects/<model("pos_auto_invoice.pos_auto_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_auto_invoice.object', {
#             'object': obj
#         })