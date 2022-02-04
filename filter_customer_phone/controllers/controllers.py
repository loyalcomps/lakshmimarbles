# -*- coding: utf-8 -*-
from odoo import http

# class FilterCustomerPhone(http.Controller):
#     @http.route('/filter_customer_phone/filter_customer_phone/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/filter_customer_phone/filter_customer_phone/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('filter_customer_phone.listing', {
#             'root': '/filter_customer_phone/filter_customer_phone',
#             'objects': http.request.env['filter_customer_phone.filter_customer_phone'].search([]),
#         })

#     @http.route('/filter_customer_phone/filter_customer_phone/objects/<model("filter_customer_phone.filter_customer_phone"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('filter_customer_phone.object', {
#             'object': obj
#         })