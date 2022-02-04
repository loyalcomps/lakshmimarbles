# -*- coding: utf-8 -*-
from odoo import http

# class AvoidBrandDupli(http.Controller):
#     @http.route('/avoid_brand_dupli/avoid_brand_dupli/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/avoid_brand_dupli/avoid_brand_dupli/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('avoid_brand_dupli.listing', {
#             'root': '/avoid_brand_dupli/avoid_brand_dupli',
#             'objects': http.request.env['avoid_brand_dupli.avoid_brand_dupli'].search([]),
#         })

#     @http.route('/avoid_brand_dupli/avoid_brand_dupli/objects/<model("avoid_brand_dupli.avoid_brand_dupli"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('avoid_brand_dupli.object', {
#             'object': obj
#         })