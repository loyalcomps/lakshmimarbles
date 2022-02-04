# -*- coding: utf-8 -*-
from odoo import http

# class PurchasePrint(http.Controller):
#     @http.route('/purchase_print/purchase_print/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_print/purchase_print/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_print.listing', {
#             'root': '/purchase_print/purchase_print',
#             'objects': http.request.env['purchase_print.purchase_print'].search([]),
#         })

#     @http.route('/purchase_print/purchase_print/objects/<model("purchase_print.purchase_print"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_print.object', {
#             'object': obj
#         })