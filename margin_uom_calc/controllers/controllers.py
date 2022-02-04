# -*- coding: utf-8 -*-
from odoo import http

# class MarginUomCalc(http.Controller):
#     @http.route('/margin_uom_calc/margin_uom_calc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/margin_uom_calc/margin_uom_calc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('margin_uom_calc.listing', {
#             'root': '/margin_uom_calc/margin_uom_calc',
#             'objects': http.request.env['margin_uom_calc.margin_uom_calc'].search([]),
#         })

#     @http.route('/margin_uom_calc/margin_uom_calc/objects/<model("margin_uom_calc.margin_uom_calc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('margin_uom_calc.object', {
#             'object': obj
#         })