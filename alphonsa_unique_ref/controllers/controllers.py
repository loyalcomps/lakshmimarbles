# -*- coding: utf-8 -*-
from odoo import http

# class AlphonsaUniqueRef(http.Controller):
#     @http.route('/alphonsa_unique_ref/alphonsa_unique_ref/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/alphonsa_unique_ref/alphonsa_unique_ref/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('alphonsa_unique_ref.listing', {
#             'root': '/alphonsa_unique_ref/alphonsa_unique_ref',
#             'objects': http.request.env['alphonsa_unique_ref.alphonsa_unique_ref'].search([]),
#         })

#     @http.route('/alphonsa_unique_ref/alphonsa_unique_ref/objects/<model("alphonsa_unique_ref.alphonsa_unique_ref"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alphonsa_unique_ref.object', {
#             'object': obj
#         })