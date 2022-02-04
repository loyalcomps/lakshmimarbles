# -*- coding: utf-8 -*-
from odoo import http

# class AccountIfscCode(http.Controller):
#     @http.route('/account_ifsc_code/account_ifsc_code/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_ifsc_code/account_ifsc_code/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_ifsc_code.listing', {
#             'root': '/account_ifsc_code/account_ifsc_code',
#             'objects': http.request.env['account_ifsc_code.account_ifsc_code'].search([]),
#         })

#     @http.route('/account_ifsc_code/account_ifsc_code/objects/<model("account_ifsc_code.account_ifsc_code"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_ifsc_code.object', {
#             'object': obj
#         })