# -*- coding: utf-8 -*-
from odoo import http

# class DaybookReport(http.Controller):
#     @http.route('/daybook_report/daybook_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/daybook_report/daybook_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('daybook_report.listing', {
#             'root': '/daybook_report/daybook_report',
#             'objects': http.request.env['daybook_report.daybook_report'].search([]),
#         })

#     @http.route('/daybook_report/daybook_report/objects/<model("daybook_report.daybook_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('daybook_report.object', {
#             'object': obj
#         })