# -*- coding: utf-8 -*-
from odoo import http

# class ExtraFieldLm(http.Controller):
#     @http.route('/extra_field_lm/extra_field_lm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/extra_field_lm/extra_field_lm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('extra_field_lm.listing', {
#             'root': '/extra_field_lm/extra_field_lm',
#             'objects': http.request.env['extra_field_lm.extra_field_lm'].search([]),
#         })

#     @http.route('/extra_field_lm/extra_field_lm/objects/<model("extra_field_lm.extra_field_lm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('extra_field_lm.object', {
#             'object': obj
#         })