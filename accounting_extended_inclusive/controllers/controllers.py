# -*- coding: utf-8 -*-
from odoo import http

# class AccountingExtendedInclusive(http.Controller):
#     @http.route('/accounting_extended_inclusive/accounting_extended_inclusive/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/accounting_extended_inclusive/accounting_extended_inclusive/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('accounting_extended_inclusive.listing', {
#             'root': '/accounting_extended_inclusive/accounting_extended_inclusive',
#             'objects': http.request.env['accounting_extended_inclusive.accounting_extended_inclusive'].search([]),
#         })

#     @http.route('/accounting_extended_inclusive/accounting_extended_inclusive/objects/<model("accounting_extended_inclusive.accounting_extended_inclusive"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('accounting_extended_inclusive.object', {
#             'object': obj
#         })