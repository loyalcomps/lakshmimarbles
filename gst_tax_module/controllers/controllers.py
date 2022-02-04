# -*- coding: utf-8 -*-
from openerp import http

# class GstTaxModule(http.Controller):
#     @http.route('/gst_tax_module/gst_tax_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gst_tax_module/gst_tax_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gst_tax_module.listing', {
#             'root': '/gst_tax_module/gst_tax_module',
#             'objects': http.request.env['gst_tax_module.gst_tax_module'].search([]),
#         })

#     @http.route('/gst_tax_module/gst_tax_module/objects/<model("gst_tax_module.gst_tax_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gst_tax_module.object', {
#             'object': obj
#         })