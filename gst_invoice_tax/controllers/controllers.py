# -*- coding: utf-8 -*-
from odoo import http

# class GstInvoiceTax(http.Controller):
#     @http.route('/gst_invoice_tax/gst_invoice_tax/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gst_invoice_tax/gst_invoice_tax/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gst_invoice_tax.listing', {
#             'root': '/gst_invoice_tax/gst_invoice_tax',
#             'objects': http.request.env['gst_invoice_tax.gst_invoice_tax'].search([]),
#         })

#     @http.route('/gst_invoice_tax/gst_invoice_tax/objects/<model("gst_invoice_tax.gst_invoice_tax"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gst_invoice_tax.object', {
#             'object': obj
#         })