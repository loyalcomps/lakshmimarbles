# -*- coding: utf-8 -*-
from odoo import http

# class PosPriceEditLog(http.Controller):
#     @http.route('/pos_price_edit_log/pos_price_edit_log/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_price_edit_log/pos_price_edit_log/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_price_edit_log.listing', {
#             'root': '/pos_price_edit_log/pos_price_edit_log',
#             'objects': http.request.env['pos_price_edit_log.pos_price_edit_log'].search([]),
#         })

#     @http.route('/pos_price_edit_log/pos_price_edit_log/objects/<model("pos_price_edit_log.pos_price_edit_log"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_price_edit_log.object', {
#             'object': obj
#         })