# -*- coding: utf-8 -*-
from odoo import http

# class AccountExtended(http.Controller):
#     @http.route('/account_extended/account_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_extended/account_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_extended.listing', {
#             'root': '/account_extended/account_extended',
#             'objects': http.request.env['account_extended.account_extended'].search([]),
#         })

#     @http.route('/account_extended/account_extended/objects/<model("account_extended.account_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_extended.object', {
#             'object': obj
#         })