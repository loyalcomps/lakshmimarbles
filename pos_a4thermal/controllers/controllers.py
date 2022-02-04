# -*- coding: utf-8 -*-
from odoo import http

# class PosA4thermal(http.Controller):
#     @http.route('/pos_a4thermal/pos_a4thermal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_a4thermal/pos_a4thermal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_a4thermal.listing', {
#             'root': '/pos_a4thermal/pos_a4thermal',
#             'objects': http.request.env['pos_a4thermal.pos_a4thermal'].search([]),
#         })

#     @http.route('/pos_a4thermal/pos_a4thermal/objects/<model("pos_a4thermal.pos_a4thermal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_a4thermal.object', {
#             'object': obj
#         })