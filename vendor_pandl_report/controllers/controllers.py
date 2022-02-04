# -*- coding: utf-8 -*-
from odoo import http

# class VendorPandlReport(http.Controller):
#     @http.route('/vendor_pandl_report/vendor_pandl_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vendor_pandl_report/vendor_pandl_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vendor_pandl_report.listing', {
#             'root': '/vendor_pandl_report/vendor_pandl_report',
#             'objects': http.request.env['vendor_pandl_report.vendor_pandl_report'].search([]),
#         })

#     @http.route('/vendor_pandl_report/vendor_pandl_report/objects/<model("vendor_pandl_report.vendor_pandl_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vendor_pandl_report.object', {
#             'object': obj
#         })