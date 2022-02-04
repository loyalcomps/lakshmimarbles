# -*- coding: utf-8 -*-
from odoo import http

# class KeralaFloodCess(http.Controller):
#     @http.route('/kerala_flood_cess/kerala_flood_cess/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kerala_flood_cess/kerala_flood_cess/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kerala_flood_cess.listing', {
#             'root': '/kerala_flood_cess/kerala_flood_cess',
#             'objects': http.request.env['kerala_flood_cess.kerala_flood_cess'].search([]),
#         })

#     @http.route('/kerala_flood_cess/kerala_flood_cess/objects/<model("kerala_flood_cess.kerala_flood_cess"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kerala_flood_cess.object', {
#             'object': obj
#         })