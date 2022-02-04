# -*- coding: utf-8 -*-
from odoo import http

# class Gstr3bReport(http.Controller):
#     @http.route('/gstr3b_report/gstr3b_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gstr3b_report/gstr3b_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gstr3b_report.listing', {
#             'root': '/gstr3b_report/gstr3b_report',
#             'objects': http.request.env['gstr3b_report.gstr3b_report'].search([]),
#         })

#     @http.route('/gstr3b_report/gstr3b_report/objects/<model("gstr3b_report.gstr3b_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gstr3b_report.object', {
#             'object': obj
#         })