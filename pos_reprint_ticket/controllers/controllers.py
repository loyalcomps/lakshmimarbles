# -*- coding: utf-8 -*-
from odoo import http

# class PosReprintTicket(http.Controller):
#     @http.route('/darupos_reprint_ticket/darupos_reprint_ticket/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/darupos_reprint_ticket/darupos_reprint_ticket/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('darupos_reprint_ticket.listing', {
#             'root': '/darupos_reprint_ticket/darupos_reprint_ticket',
#             'objects': http.request.env['darupos_reprint_ticket.darupos_reprint_ticket'].search([]),
#         })

#     @http.route('/darupos_reprint_ticket/darupos_reprint_ticket/objects/<model("darupos_reprint_ticket.darupos_reprint_ticket"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('darupos_reprint_ticket.object', {
#             'object': obj
#         })