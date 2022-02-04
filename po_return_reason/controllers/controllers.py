# -*- coding: utf-8 -*-
from odoo import http

# class PoReturnReason(http.Controller):
#     @http.route('/po_return_reason/po_return_reason/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/po_return_reason/po_return_reason/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('po_return_reason.listing', {
#             'root': '/po_return_reason/po_return_reason',
#             'objects': http.request.env['po_return_reason.po_return_reason'].search([]),
#         })

#     @http.route('/po_return_reason/po_return_reason/objects/<model("po_return_reason.po_return_reason"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('po_return_reason.object', {
#             'object': obj
#         })