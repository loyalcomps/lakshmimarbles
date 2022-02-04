# -*- coding: utf-8 -*-
from odoo import http

# class PosMrpSalepriceCheck(http.Controller):
#     @http.route('/pos_mrp_saleprice_check/pos_mrp_saleprice_check/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_mrp_saleprice_check/pos_mrp_saleprice_check/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_mrp_saleprice_check.listing', {
#             'root': '/pos_mrp_saleprice_check/pos_mrp_saleprice_check',
#             'objects': http.request.env['pos_mrp_saleprice_check.pos_mrp_saleprice_check'].search([]),
#         })

#     @http.route('/pos_mrp_saleprice_check/pos_mrp_saleprice_check/objects/<model("pos_mrp_saleprice_check.pos_mrp_saleprice_check"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_mrp_saleprice_check.object', {
#             'object': obj
#         })