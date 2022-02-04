# -*- coding: utf-8 -*-
from odoo import http

# class SalePurchaseDiscount(http.Controller):
#     @http.route('/sale_purchase_discount/sale_purchase_discount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_purchase_discount/sale_purchase_discount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_purchase_discount.listing', {
#             'root': '/sale_purchase_discount/sale_purchase_discount',
#             'objects': http.request.env['sale_purchase_discount.sale_purchase_discount'].search([]),
#         })

#     @http.route('/sale_purchase_discount/sale_purchase_discount/objects/<model("sale_purchase_discount.sale_purchase_discount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_purchase_discount.object', {
#             'object': obj
#         })