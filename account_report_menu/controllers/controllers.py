# -*- coding: utf-8 -*-
from odoo import http

# class ReportHeadAccount(http.Controller):
#     @http.route('/report_head_account/report_head_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_head_account/report_head_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_head_account.listing', {
#             'root': '/report_head_account/report_head_account',
#             'objects': http.request.env['report_head_account.report_head_account'].search([]),
#         })

#     @http.route('/report_head_account/report_head_account/objects/<model("report_head_account.report_head_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_head_account.object', {
#             'object': obj
#         })