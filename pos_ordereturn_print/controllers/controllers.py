# -*- coding: utf-8 -*-
from odoo import http

# class PosSalesreturnPrint(http.Controller):
#     @http.route('/pos_salesreturn_print/pos_salesreturn_print/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_salesreturn_print/pos_salesreturn_print/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_salesreturn_print.listing', {
#             'root': '/pos_salesreturn_print/pos_salesreturn_print',
#             'objects': http.request.env['pos_salesreturn_print.pos_salesreturn_print'].search([]),
#         })

#     @http.route('/pos_salesreturn_print/pos_salesreturn_print/objects/<model("pos_salesreturn_print.pos_salesreturn_print"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_salesreturn_print.object', {
#             'object': obj
#         })