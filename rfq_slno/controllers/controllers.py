# -*- coding: utf-8 -*-
from odoo import http

# class RfqSlno(http.Controller):
#     @http.route('/rfq_slno/rfq_slno/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rfq_slno/rfq_slno/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rfq_slno.listing', {
#             'root': '/rfq_slno/rfq_slno',
#             'objects': http.request.env['rfq_slno.rfq_slno'].search([]),
#         })

#     @http.route('/rfq_slno/rfq_slno/objects/<model("rfq_slno.rfq_slno"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rfq_slno.object', {
#             'object': obj
#         })