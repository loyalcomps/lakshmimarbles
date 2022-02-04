# -*- coding: utf-8 -*-
from odoo import http

# class ChequeManagement(http.Controller):
#     @http.route('/cheque_management/cheque_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cheque_management/cheque_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cheque_management.listing', {
#             'root': '/cheque_management/cheque_management',
#             'objects': http.request.env['cheque_management.cheque_management'].search([]),
#         })

#     @http.route('/cheque_management/cheque_management/objects/<model("cheque_management.cheque_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cheque_management.object', {
#             'object': obj
#         })