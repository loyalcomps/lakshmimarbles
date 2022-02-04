# -*- coding: utf-8 -*-
from odoo import http

# class SessionAmount(http.Controller):
#     @http.route('/session_amount/session_amount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/session_amount/session_amount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('session_amount.listing', {
#             'root': '/session_amount/session_amount',
#             'objects': http.request.env['session_amount.session_amount'].search([]),
#         })

#     @http.route('/session_amount/session_amount/objects/<model("session_amount.session_amount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('session_amount.object', {
#             'object': obj
#         })