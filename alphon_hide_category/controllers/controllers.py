# -*- coding: utf-8 -*-
from odoo import http

# class AlphonHideCategory(http.Controller):
#     @http.route('/alphon_hide_category/alphon_hide_category/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/alphon_hide_category/alphon_hide_category/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('alphon_hide_category.listing', {
#             'root': '/alphon_hide_category/alphon_hide_category',
#             'objects': http.request.env['alphon_hide_category.alphon_hide_category'].search([]),
#         })

#     @http.route('/alphon_hide_category/alphon_hide_category/objects/<model("alphon_hide_category.alphon_hide_category"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alphon_hide_category.object', {
#             'object': obj
#         })