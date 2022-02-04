# -*- coding: utf-8 -*-
from odoo import http

# class ReortGeneralLedger(http.Controller):
#     @http.route('/report_general_ledger/report_general_ledger/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_general_ledger/report_general_ledger/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('reort_general_ledger.listing', {
#             'root': '/report_general_ledger/report_general_ledger',
#             'objects': http.request.env['report_general_ledger.report_general_ledger'].search([]),
#         })

#     @http.route('/report_general_ledger/report_general_ledger/objects/<model("report_general_ledger.report_general_ledger"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reort_general_ledger.object', {
#             'object': obj
#         })