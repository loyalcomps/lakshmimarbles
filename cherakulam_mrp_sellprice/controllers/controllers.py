# -*- coding: utf-8 -*-
from odoo import http

# class CherakulamMrpSellprice(http.Controller):
#     @http.route('/cherakulam_mrp_sellprice/cherakulam_mrp_sellprice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cherakulam_mrp_sellprice/cherakulam_mrp_sellprice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cherakulam_mrp_sellprice.listing', {
#             'root': '/cherakulam_mrp_sellprice/cherakulam_mrp_sellprice',
#             'objects': http.request.env['cherakulam_mrp_sellprice.cherakulam_mrp_sellprice'].search([]),
#         })

#     @http.route('/cherakulam_mrp_sellprice/cherakulam_mrp_sellprice/objects/<model("cherakulam_mrp_sellprice.cherakulam_mrp_sellprice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cherakulam_mrp_sellprice.object', {
#             'object': obj
#         })