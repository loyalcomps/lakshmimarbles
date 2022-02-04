# -*- coding: utf-8 -*-
from odoo import http

# class QltyPosReprint(http.Controller):
#     @http.route('/qlty_pos_reprint/qlty_pos_reprint/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/qlty_pos_reprint/qlty_pos_reprint/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('qlty_pos_reprint.listing', {
#             'root': '/qlty_pos_reprint/qlty_pos_reprint',
#             'objects': http.request.env['qlty_pos_reprint.qlty_pos_reprint'].search([]),
#         })

#     @http.route('/qlty_pos_reprint/qlty_pos_reprint/objects/<model("qlty_pos_reprint.qlty_pos_reprint"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('qlty_pos_reprint.object', {
#             'object': obj
#         })