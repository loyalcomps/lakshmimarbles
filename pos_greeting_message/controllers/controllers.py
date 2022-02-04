# -*- coding: utf-8 -*-
from odoo import http

# class PosGreetingMessage(http.Controller):
#     @http.route('/pos_greeting_message/pos_greeting_message/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_greeting_message/pos_greeting_message/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_greeting_message.listing', {
#             'root': '/pos_greeting_message/pos_greeting_message',
#             'objects': http.request.env['pos_greeting_message.pos_greeting_message'].search([]),
#         })

#     @http.route('/pos_greeting_message/pos_greeting_message/objects/<model("pos_greeting_message.pos_greeting_message"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_greeting_message.object', {
#             'object': obj
#         })