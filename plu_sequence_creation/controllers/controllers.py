# -*- coding: utf-8 -*-
from odoo import http

# class PluSequenceCreation(http.Controller):
#     @http.route('/plu_sequence_creation/plu_sequence_creation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/plu_sequence_creation/plu_sequence_creation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('plu_sequence_creation.listing', {
#             'root': '/plu_sequence_creation/plu_sequence_creation',
#             'objects': http.request.env['plu_sequence_creation.plu_sequence_creation'].search([]),
#         })

#     @http.route('/plu_sequence_creation/plu_sequence_creation/objects/<model("plu_sequence_creation.plu_sequence_creation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('plu_sequence_creation.object', {
#             'object': obj
#         })