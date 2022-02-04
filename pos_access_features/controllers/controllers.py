# -*- coding: utf-8 -*-
from odoo import http

# class PosAccessFeatures(http.Controller):
#     @http.route('/pos_access_features/pos_access_features/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_access_features/pos_access_features/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_access_features.listing', {
#             'root': '/pos_access_features/pos_access_features',
#             'objects': http.request.env['pos_access_features.pos_access_features'].search([]),
#         })

#     @http.route('/pos_access_features/pos_access_features/objects/<model("pos_access_features.pos_access_features"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_access_features.object', {
#             'object': obj
#         })