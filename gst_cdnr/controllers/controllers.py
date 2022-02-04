# -*- coding: utf-8 -*-
from odoo import http

# class GstCdnr(http.Controller):
#     @http.route('/gst_cdnr/gst_cdnr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gst_cdnr/gst_cdnr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gst_cdnr.listing', {
#             'root': '/gst_cdnr/gst_cdnr',
#             'objects': http.request.env['gst_cdnr.gst_cdnr'].search([]),
#         })

#     @http.route('/gst_cdnr/gst_cdnr/objects/<model("gst_cdnr.gst_cdnr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gst_cdnr.object', {
#             'object': obj
#         })