# -*- coding: utf-8 -*-
from odoo import http

# class Buy3Get1(http.Controller):
#     @http.route('/buy3_get1/buy3_get1/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/buy3_get1/buy3_get1/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('buy3_get1.listing', {
#             'root': '/buy3_get1/buy3_get1',
#             'objects': http.request.env['buy3_get1.buy3_get1'].search([]),
#         })

#     @http.route('/buy3_get1/buy3_get1/objects/<model("buy3_get1.buy3_get1"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('buy3_get1.object', {
#             'object': obj
#         })