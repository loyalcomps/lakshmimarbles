# -*- coding: utf-8 -*-
from odoo import http

# class UserLandingcost(http.Controller):
#     @http.route('/user_landingcost/user_landingcost/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/user_landingcost/user_landingcost/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('user_landingcost.listing', {
#             'root': '/user_landingcost/user_landingcost',
#             'objects': http.request.env['user_landingcost.user_landingcost'].search([]),
#         })

#     @http.route('/user_landingcost/user_landingcost/objects/<model("user_landingcost.user_landingcost"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('user_landingcost.object', {
#             'object': obj
#         })