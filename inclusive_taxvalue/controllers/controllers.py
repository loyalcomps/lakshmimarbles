# -*- coding: utf-8 -*-
from odoo import http

# class InclusiveTaxvalue(http.Controller):
#     @http.route('/inclusive_taxvalue/inclusive_taxvalue/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inclusive_taxvalue/inclusive_taxvalue/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inclusive_taxvalue.listing', {
#             'root': '/inclusive_taxvalue/inclusive_taxvalue',
#             'objects': http.request.env['inclusive_taxvalue.inclusive_taxvalue'].search([]),
#         })

#     @http.route('/inclusive_taxvalue/inclusive_taxvalue/objects/<model("inclusive_taxvalue.inclusive_taxvalue"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inclusive_taxvalue.object', {
#             'object': obj
#         })