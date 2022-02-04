# -*- coding: utf-8 -*-
from odoo import http

# class CustomerBarcodeSettings(http.Controller):
#     @http.route('/customer_barcode_settings/customer_barcode_settings/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_barcode_settings/customer_barcode_settings/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_barcode_settings.listing', {
#             'root': '/customer_barcode_settings/customer_barcode_settings',
#             'objects': http.request.env['customer_barcode_settings.customer_barcode_settings'].search([]),
#         })

#     @http.route('/customer_barcode_settings/customer_barcode_settings/objects/<model("customer_barcode_settings.customer_barcode_settings"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_barcode_settings.object', {
#             'object': obj
#         })