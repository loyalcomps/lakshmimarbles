# -*- coding: utf-8 -*-
from odoo import http

# class InternalTransferExtended(http.Controller):
#     @http.route('/internal_transfer_extended/internal_transfer_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/internal_transfer_extended/internal_transfer_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('internal_transfer_extended.listing', {
#             'root': '/internal_transfer_extended/internal_transfer_extended',
#             'objects': http.request.env['internal_transfer_extended.internal_transfer_extended'].search([]),
#         })

#     @http.route('/internal_transfer_extended/internal_transfer_extended/objects/<model("internal_transfer_extended.internal_transfer_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('internal_transfer_extended.object', {
#             'object': obj
#         })