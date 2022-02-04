# -*- coding: utf-8 -*-
from odoo import http

# class PosRoundoff(http.Controller):
#     @http.route('/pos_roundoff/pos_roundoff/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_roundoff/pos_roundoff/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_roundoff.listing', {
#             'root': '/pos_roundoff/pos_roundoff',
#             'objects': http.request.env['pos_roundoff.pos_roundoff'].search([]),
#         })

#     @http.route('/pos_roundoff/pos_roundoff/objects/<model("pos_roundoff.pos_roundoff"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_roundoff.object', {
#             'object': obj
#         })