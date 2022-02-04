# -*- coding: utf-8 -*-
from odoo import http

# class HideHsnSacCode(http.Controller):
#     @http.route('/hide_hsn_sac_code/hide_hsn_sac_code/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hide_hsn_sac_code/hide_hsn_sac_code/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hide_hsn_sac_code.listing', {
#             'root': '/hide_hsn_sac_code/hide_hsn_sac_code',
#             'objects': http.request.env['hide_hsn_sac_code.hide_hsn_sac_code'].search([]),
#         })

#     @http.route('/hide_hsn_sac_code/hide_hsn_sac_code/objects/<model("hide_hsn_sac_code.hide_hsn_sac_code"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hide_hsn_sac_code.object', {
#             'object': obj
#         })