# -*- coding: utf-8 -*-
from odoo import http

# class VendorBillPaymentTerm(http.Controller):
#     @http.route('/vendor_bill_payment_term/vendor_bill_payment_term/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vendor_bill_payment_term/vendor_bill_payment_term/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vendor_bill_payment_term.listing', {
#             'root': '/vendor_bill_payment_term/vendor_bill_payment_term',
#             'objects': http.request.env['vendor_bill_payment_term.vendor_bill_payment_term'].search([]),
#         })

#     @http.route('/vendor_bill_payment_term/vendor_bill_payment_term/objects/<model("vendor_bill_payment_term.vendor_bill_payment_term"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vendor_bill_payment_term.object', {
#             'object': obj
#         })