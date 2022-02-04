# -*- coding: utf-8 -*-
from odoo import http

# class NatureSell(http.Controller):
#     @http.route('/nature_sell/nature_sell/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nature_sell/nature_sell/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nature_sell.listing', {
#             'root': '/nature_sell/nature_sell',
#             'objects': http.request.env['nature_sell.nature_sell'].search([]),
#         })

#     @http.route('/nature_sell/nature_sell/objects/<model("nature_sell.nature_sell"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nature_sell.object', {
#             'object': obj
#         })