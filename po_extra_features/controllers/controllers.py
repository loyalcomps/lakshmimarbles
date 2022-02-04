# -*- coding: utf-8 -*-
from odoo import http

# class PoExtraFeatures(http.Controller):
#     @http.route('/po_extra_features/po_extra_features/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/po_extra_features/po_extra_features/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('po_extra_features.listing', {
#             'root': '/po_extra_features/po_extra_features',
#             'objects': http.request.env['po_extra_features.po_extra_features'].search([]),
#         })

#     @http.route('/po_extra_features/po_extra_features/objects/<model("po_extra_features.po_extra_features"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('po_extra_features.object', {
#             'object': obj
#         })