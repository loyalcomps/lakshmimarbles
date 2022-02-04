# -*- coding: utf-8 -*-
from odoo import http

# class MfCashControl(http.Controller):
#     @http.route('/mf_cash_control/mf_cash_control/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mf_cash_control/mf_cash_control/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mf_cash_control.listing', {
#             'root': '/mf_cash_control/mf_cash_control',
#             'objects': http.request.env['mf_cash_control.mf_cash_control'].search([]),
#         })

#     @http.route('/mf_cash_control/mf_cash_control/objects/<model("mf_cash_control.mf_cash_control"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mf_cash_control.object', {
#             'object': obj
#         })