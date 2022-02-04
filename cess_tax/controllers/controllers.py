# -*- coding: utf-8 -*-
from odoo import http

# class CessTax(http.Controller):
#     @http.route('/cess_tax/cess_tax/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cess_tax/cess_tax/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cess_tax.listing', {
#             'root': '/cess_tax/cess_tax',
#             'objects': http.request.env['cess_tax.cess_tax'].search([]),
#         })

#     @http.route('/cess_tax/cess_tax/objects/<model("cess_tax.cess_tax"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cess_tax.object', {
#             'object': obj
#         })