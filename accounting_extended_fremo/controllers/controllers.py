# -*- coding: utf-8 -*-
from odoo import http

# class AccountingExtendedFremo(http.Controller):
#     @http.route('/accounting_extended_fremo/accounting_extended_fremo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/accounting_extended_fremo/accounting_extended_fremo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('accounting_extended_fremo.listing', {
#             'root': '/accounting_extended_fremo/accounting_extended_fremo',
#             'objects': http.request.env['accounting_extended_fremo.accounting_extended_fremo'].search([]),
#         })

#     @http.route('/accounting_extended_fremo/accounting_extended_fremo/objects/<model("accounting_extended_fremo.accounting_extended_fremo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('accounting_extended_fremo.object', {
#             'object': obj
#         })