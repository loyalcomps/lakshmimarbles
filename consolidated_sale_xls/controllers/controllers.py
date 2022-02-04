# -*- coding: utf-8 -*-
from odoo import http

# class ConsolidatedSaleReport(http.Controller):
#     @http.route('/consolidated_sale_report/consolidated_sale_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/consolidated_sale_report/consolidated_sale_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('consolidated_sale_report.listing', {
#             'root': '/consolidated_sale_report/consolidated_sale_report',
#             'objects': http.request.env['consolidated_sale_report.consolidated_sale_report'].search([]),
#         })

#     @http.route('/consolidated_sale_report/consolidated_sale_report/objects/<model("consolidated_sale_report.consolidated_sale_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('consolidated_sale_report.object', {
#             'object': obj
#         })