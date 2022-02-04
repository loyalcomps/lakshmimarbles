# -*- coding: utf-8 -*-
from odoo import http

# class ClosingValueRestriction(http.Controller):
#     @http.route('/closing_value_restriction/closing_value_restriction/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/closing_value_restriction/closing_value_restriction/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('closing_value_restriction.listing', {
#             'root': '/closing_value_restriction/closing_value_restriction',
#             'objects': http.request.env['closing_value_restriction.closing_value_restriction'].search([]),
#         })

#     @http.route('/closing_value_restriction/closing_value_restriction/objects/<model("closing_value_restriction.closing_value_restriction"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('closing_value_restriction.object', {
#             'object': obj
#         })