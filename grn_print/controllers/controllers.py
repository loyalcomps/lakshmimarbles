# -*- coding: utf-8 -*-
from odoo import http

# class GrnPrint(http.Controller):
#     @http.route('/grn_print/grn_print/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/grn_print/grn_print/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('grn_print.listing', {
#             'root': '/grn_print/grn_print',
#             'objects': http.request.env['grn_print.grn_print'].search([]),
#         })

#     @http.route('/grn_print/grn_print/objects/<model("grn_print.grn_print"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('grn_print.object', {
#             'object': obj
#         })