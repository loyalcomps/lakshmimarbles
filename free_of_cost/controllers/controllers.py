# -*- coding: utf-8 -*-
from odoo import http

# class FreeOfCost(http.Controller):
#     @http.route('/free_of_cost/free_of_cost/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/free_of_cost/free_of_cost/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('free_of_cost.listing', {
#             'root': '/free_of_cost/free_of_cost',
#             'objects': http.request.env['free_of_cost.free_of_cost'].search([]),
#         })

#     @http.route('/free_of_cost/free_of_cost/objects/<model("free_of_cost.free_of_cost"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('free_of_cost.object', {
#             'object': obj
#         })