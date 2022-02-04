# -*- coding: utf-8 -*-
from odoo import http

# class PosItemCount(http.Controller):
#     @http.route('/pos_item_count/pos_item_count/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_item_count/pos_item_count/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_item_count.listing', {
#             'root': '/pos_item_count/pos_item_count',
#             'objects': http.request.env['pos_item_count.pos_item_count'].search([]),
#         })

#     @http.route('/pos_item_count/pos_item_count/objects/<model("pos_item_count.pos_item_count"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_item_count.object', {
#             'object': obj
#         })