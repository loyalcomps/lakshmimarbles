# -*- coding: utf-8 -*-
from odoo import http

# class PosCombopack(http.Controller):
#     @http.route('/pos_combopack/pos_combopack/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_combopack/pos_combopack/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_combopack.listing', {
#             'root': '/pos_combopack/pos_combopack',
#             'objects': http.request.env['pos_combopack.pos_combopack'].search([]),
#         })

#     @http.route('/pos_combopack/pos_combopack/objects/<model("pos_combopack.pos_combopack"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_combopack.object', {
#             'object': obj
#         })