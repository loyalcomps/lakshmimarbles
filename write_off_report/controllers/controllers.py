# -*- coding: utf-8 -*-
from odoo import http

# class WriteOffReport(http.Controller):
#     @http.route('/write_off_report/write_off_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/write_off_report/write_off_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('write_off_report.listing', {
#             'root': '/write_off_report/write_off_report',
#             'objects': http.request.env['write_off_report.write_off_report'].search([]),
#         })

#     @http.route('/write_off_report/write_off_report/objects/<model("write_off_report.write_off_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('write_off_report.object', {
#             'object': obj
#         })