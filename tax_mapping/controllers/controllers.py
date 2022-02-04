# -*- coding: utf-8 -*-
from odoo import http

# class TaxMapping(http.Controller):
#     @http.route('/tax_mapping/tax_mapping/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tax_mapping/tax_mapping/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tax_mapping.listing', {
#             'root': '/tax_mapping/tax_mapping',
#             'objects': http.request.env['tax_mapping.tax_mapping'].search([]),
#         })

#     @http.route('/tax_mapping/tax_mapping/objects/<model("tax_mapping.tax_mapping"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tax_mapping.object', {
#             'object': obj
#         })