# -*- coding: utf-8 -*-
from odoo import http

# class CustomerUnique(http.Controller):
#     @http.route('/customer_unique/customer_unique/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_unique/customer_unique/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_unique.listing', {
#             'root': '/customer_unique/customer_unique',
#             'objects': http.request.env['customer_unique.customer_unique'].search([]),
#         })

#     @http.route('/customer_unique/customer_unique/objects/<model("customer_unique.customer_unique"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_unique.object', {
#             'object': obj
#         })