# -*- coding: utf-8 -*-
from odoo import http

# class PosSalesperson(http.Controller):
#     @http.route('/pos_salesperson/pos_salesperson/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_salesperson/pos_salesperson/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_salesperson.listing', {
#             'root': '/pos_salesperson/pos_salesperson',
#             'objects': http.request.env['pos_salesperson.pos_salesperson'].search([]),
#         })

#     @http.route('/pos_salesperson/pos_salesperson/objects/<model("pos_salesperson.pos_salesperson"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_salesperson.object', {
#             'object': obj
#         })