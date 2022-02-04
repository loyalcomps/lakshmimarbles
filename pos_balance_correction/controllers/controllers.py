# -*- coding: utf-8 -*-
from odoo import http

# class PosBalanceCorrection(http.Controller):
#     @http.route('/pos_balance_correction/pos_balance_correction/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_balance_correction/pos_balance_correction/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_balance_correction.listing', {
#             'root': '/pos_balance_correction/pos_balance_correction',
#             'objects': http.request.env['pos_balance_correction.pos_balance_correction'].search([]),
#         })

#     @http.route('/pos_balance_correction/pos_balance_correction/objects/<model("pos_balance_correction.pos_balance_correction"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_balance_correction.object', {
#             'object': obj
#         })