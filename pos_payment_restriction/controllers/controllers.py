# -*- coding: utf-8 -*-
from odoo import http

# class PosPaymentRestriction(http.Controller):
#     @http.route('/pos_payment_restriction/pos_payment_restriction/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_payment_restriction/pos_payment_restriction/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_payment_restriction.listing', {
#             'root': '/pos_payment_restriction/pos_payment_restriction',
#             'objects': http.request.env['pos_payment_restriction.pos_payment_restriction'].search([]),
#         })

#     @http.route('/pos_payment_restriction/pos_payment_restriction/objects/<model("pos_payment_restriction.pos_payment_restriction"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_payment_restriction.object', {
#             'object': obj
#         })