# -*- coding: utf-8 -*-
from odoo import http

# class PosAutoPhone(http.Controller):
#     @http.route('/pos_auto_phone/pos_auto_phone/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_auto_phone/pos_auto_phone/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_auto_phone.listing', {
#             'root': '/pos_auto_phone/pos_auto_phone',
#             'objects': http.request.env['pos_auto_phone.pos_auto_phone'].search([]),
#         })

#     @http.route('/pos_auto_phone/pos_auto_phone/objects/<model("pos_auto_phone.pos_auto_phone"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_auto_phone.object', {
#             'object': obj
#         })