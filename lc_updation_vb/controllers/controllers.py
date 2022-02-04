# -*- coding: utf-8 -*-
from odoo import http

# class LcUpdationVb(http.Controller):
#     @http.route('/lc_updation_vb/lc_updation_vb/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lc_updation_vb/lc_updation_vb/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lc_updation_vb.listing', {
#             'root': '/lc_updation_vb/lc_updation_vb',
#             'objects': http.request.env['lc_updation_vb.lc_updation_vb'].search([]),
#         })

#     @http.route('/lc_updation_vb/lc_updation_vb/objects/<model("lc_updation_vb.lc_updation_vb"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lc_updation_vb.object', {
#             'object': obj
#         })