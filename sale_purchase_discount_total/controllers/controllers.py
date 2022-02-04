# -*- coding: utf-8 -*-
from odoo import http

# class SalePurchaseDiscountTotal(http.Controller):
#     @http.route('/sale_purchase_discount_total/sale_purchase_discount_total/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_purchase_discount_total/sale_purchase_discount_total/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_purchase_discount_total.listing', {
#             'root': '/sale_purchase_discount_total/sale_purchase_discount_total',
#             'objects': http.request.env['sale_purchase_discount_total.sale_purchase_discount_total'].search([]),
#         })

#     @http.route('/sale_purchase_discount_total/sale_purchase_discount_total/objects/<model("sale_purchase_discount_total.sale_purchase_discount_total"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_purchase_discount_total.object', {
#             'object': obj
#         })