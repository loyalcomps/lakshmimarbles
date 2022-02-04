# -*- coding: utf-8 -*-
from odoo import http

# class ReportPartnerLedger(http.Controller):
#     @http.route('/report_partner_ledger/report_partner_ledger/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_partner_ledger/report_partner_ledger/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_partner_ledger.listing', {
#             'root': '/report_partner_ledger/report_partner_ledger',
#             'objects': http.request.env['report_partner_ledger.report_partner_ledger'].search([]),
#         })

#     @http.route('/report_partner_ledger/report_partner_ledger/objects/<model("report_partner_ledger.report_partner_ledger"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_partner_ledger.object', {
#             'object': obj
#         })