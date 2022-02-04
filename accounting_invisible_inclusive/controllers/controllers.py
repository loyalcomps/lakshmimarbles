# -*- coding: utf-8 -*-
from odoo import http

# class AccountingInvisibleInclusive(http.Controller):
#     @http.route('/accounting_invisible_inclusive/accounting_invisible_inclusive/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/accounting_invisible_inclusive/accounting_invisible_inclusive/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('accounting_invisible_inclusive.listing', {
#             'root': '/accounting_invisible_inclusive/accounting_invisible_inclusive',
#             'objects': http.request.env['accounting_invisible_inclusive.accounting_invisible_inclusive'].search([]),
#         })

#     @http.route('/accounting_invisible_inclusive/accounting_invisible_inclusive/objects/<model("accounting_invisible_inclusive.accounting_invisible_inclusive"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('accounting_invisible_inclusive.object', {
#             'object': obj
#         })