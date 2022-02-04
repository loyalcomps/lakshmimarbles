# -*- coding: utf-8 -*-
from odoo import http

# class PosOperatingUnit(http.Controller):
#     @http.route('/pos_operating_unit/pos_operating_unit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_operating_unit/pos_operating_unit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_operating_unit.listing', {
#             'root': '/pos_operating_unit/pos_operating_unit',
#             'objects': http.request.env['pos_operating_unit.pos_operating_unit'].search([]),
#         })

#     @http.route('/pos_operating_unit/pos_operating_unit/objects/<model("pos_operating_unit.pos_operating_unit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_operating_unit.object', {
#             'object': obj
#         })