# -*- coding: utf-8 -*-
from odoo import http

# class PosUomProduct(http.Controller):
#     @http.route('/pos_uom_product/pos_uom_product/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_uom_product/pos_uom_product/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_uom_product.listing', {
#             'root': '/pos_uom_product/pos_uom_product',
#             'objects': http.request.env['pos_uom_product.pos_uom_product'].search([]),
#         })

#     @http.route('/pos_uom_product/pos_uom_product/objects/<model("pos_uom_product.pos_uom_product"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_uom_product.object', {
#             'object': obj
#         })