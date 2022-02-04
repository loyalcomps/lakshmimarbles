# -*- coding: utf-8 -*-
from odoo import http

# class LoyalPosUserrights(http.Controller):
#     @http.route('/loyal_pos_userrights/loyal_pos_userrights/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/loyal_pos_userrights/loyal_pos_userrights/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('loyal_pos_userrights.listing', {
#             'root': '/loyal_pos_userrights/loyal_pos_userrights',
#             'objects': http.request.env['loyal_pos_userrights.loyal_pos_userrights'].search([]),
#         })

#     @http.route('/loyal_pos_userrights/loyal_pos_userrights/objects/<model("loyal_pos_userrights.loyal_pos_userrights"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('loyal_pos_userrights.object', {
#             'object': obj
#         })