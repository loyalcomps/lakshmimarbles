# -*- coding: utf-8 -*-
from odoo import http

# class SaleApproval(http.Controller):
#     @http.route('/sale_approval/sale_approval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_approval/sale_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_approval.listing', {
#             'root': '/sale_approval/sale_approval',
#             'objects': http.request.env['sale_approval.sale_approval'].search([]),
#         })

#     @http.route('/sale_approval/sale_approval/objects/<model("sale_approval.sale_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_approval.object', {
#             'object': obj
#         })