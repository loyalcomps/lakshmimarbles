# -*- coding: utf-8 -*-
from odoo import http

# class VendorPriceUnchange(http.Controller):
#     @http.route('/vendor_price_unchange/vendor_price_unchange/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vendor_price_unchange/vendor_price_unchange/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vendor_price_unchange.listing', {
#             'root': '/vendor_price_unchange/vendor_price_unchange',
#             'objects': http.request.env['vendor_price_unchange.vendor_price_unchange'].search([]),
#         })

#     @http.route('/vendor_price_unchange/vendor_price_unchange/objects/<model("vendor_price_unchange.vendor_price_unchange"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vendor_price_unchange.object', {
#             'object': obj
#         })