# -*- coding: utf-8 -*-
from odoo import http

# class PosKeyboardShort(http.Controller):
#     @http.route('/pos_keyboard_short/pos_keyboard_short/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_keyboard_short/pos_keyboard_short/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_keyboard_short.listing', {
#             'root': '/pos_keyboard_short/pos_keyboard_short',
#             'objects': http.request.env['pos_keyboard_short.pos_keyboard_short'].search([]),
#         })

#     @http.route('/pos_keyboard_short/pos_keyboard_short/objects/<model("pos_keyboard_short.pos_keyboard_short"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_keyboard_short.object', {
#             'object': obj
#         })