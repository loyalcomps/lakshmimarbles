# -*- coding: utf-8 -*-
from odoo import http

# class GrandSaleDetailXls(http.Controller):
#     @http.route('/grand_sale_detail_xls/grand_sale_detail_xls/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/grand_sale_detail_xls/grand_sale_detail_xls/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('grand_sale_detail_xls.listing', {
#             'root': '/grand_sale_detail_xls/grand_sale_detail_xls',
#             'objects': http.request.env['grand_sale_detail_xls.grand_sale_detail_xls'].search([]),
#         })

#     @http.route('/grand_sale_detail_xls/grand_sale_detail_xls/objects/<model("grand_sale_detail_xls.grand_sale_detail_xls"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('grand_sale_detail_xls.object', {
#             'object': obj
#         })