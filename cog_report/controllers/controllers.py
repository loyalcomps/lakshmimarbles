# -*- coding: utf-8 -*-
from odoo import http

# class CogReport(http.Controller):
#     @http.route('/cog_report/cog_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cog_report/cog_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cog_report.listing', {
#             'root': '/cog_report/cog_report',
#             'objects': http.request.env['cog_report.cog_report'].search([]),
#         })

#     @http.route('/cog_report/cog_report/objects/<model("cog_report.cog_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cog_report.object', {
#             'object': obj
#         })