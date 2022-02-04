# -*- coding: utf-8 -*-
from odoo import http

# class TaxAdjust(http.Controller):
#     @http.route('/tax_adjust/tax_adjust/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tax_adjust/tax_adjust/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tax_adjust.listing', {
#             'root': '/tax_adjust/tax_adjust',
#             'objects': http.request.env['tax_adjust.tax_adjust'].search([]),
#         })

#     @http.route('/tax_adjust/tax_adjust/objects/<model("tax_adjust.tax_adjust"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tax_adjust.object', {
#             'object': obj
#         })