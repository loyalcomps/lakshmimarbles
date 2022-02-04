# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
from odoo import http

# class Bookstore(http.Controller):
#     @http.route('/texbyte_gst/texbyte_gst/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/texbyte_gst/texbyte_gst/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('texbyte_gst.listing', {
#             'root': '/texbyte_gst/texbyte_gst',
#             'objects': http.request.env['texbyte_gst.texbyte_gst'].search([]),
#         })

#     @http.route('/texbyte_gst/texbyte_gst/objects/<model("texbyte_gst.texbyte_gst"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('texbyte_gst.object', {
#             'object': obj
#         })
