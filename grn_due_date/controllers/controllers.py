# -*- coding: utf-8 -*-
from odoo import http

# class GrnDueDate(http.Controller):
#     @http.route('/grn_due_date/grn_due_date/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/grn_due_date/grn_due_date/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('grn_due_date.listing', {
#             'root': '/grn_due_date/grn_due_date',
#             'objects': http.request.env['grn_due_date.grn_due_date'].search([]),
#         })

#     @http.route('/grn_due_date/grn_due_date/objects/<model("grn_due_date.grn_due_date"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('grn_due_date.object', {
#             'object': obj
#         })