# -*- coding: utf-8 -*-
from odoo import http

# class SuperUser(http.Controller):
#     @http.route('/super_user/super_user/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/super_user/super_user/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('super_user.listing', {
#             'root': '/super_user/super_user',
#             'objects': http.request.env['super_user.super_user'].search([]),
#         })

#     @http.route('/super_user/super_user/objects/<model("super_user.super_user"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('super_user.object', {
#             'object': obj
#         })