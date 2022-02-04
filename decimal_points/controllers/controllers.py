# -*- coding: utf-8 -*-
from odoo import http

# class DecimalPoints(http.Controller):
#     @http.route('/decimal_points/decimal_points/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/decimal_points/decimal_points/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('decimal_points.listing', {
#             'root': '/decimal_points/decimal_points',
#             'objects': http.request.env['decimal_points.decimal_points'].search([]),
#         })

#     @http.route('/decimal_points/decimal_points/objects/<model("decimal_points.decimal_points"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('decimal_points.object', {
#             'object': obj
#         })