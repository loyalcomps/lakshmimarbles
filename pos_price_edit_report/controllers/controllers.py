# -*- coding: utf-8 -*-
from odoo import http

# class PosPriceEditReport(http.Controller):
#     @http.route('/pos_price_edit_report/pos_price_edit_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_price_edit_report/pos_price_edit_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_price_edit_report.listing', {
#             'root': '/pos_price_edit_report/pos_price_edit_report',
#             'objects': http.request.env['pos_price_edit_report.pos_price_edit_report'].search([]),
#         })

#     @http.route('/pos_price_edit_report/pos_price_edit_report/objects/<model("pos_price_edit_report.pos_price_edit_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_price_edit_report.object', {
#             'object': obj
#         })