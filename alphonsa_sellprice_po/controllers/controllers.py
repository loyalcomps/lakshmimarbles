# -*- coding: utf-8 -*-
from odoo import http

# class AlphonsaSellpricePo(http.Controller):
#     @http.route('/alphonsa_sellprice_po/alphonsa_sellprice_po/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/alphonsa_sellprice_po/alphonsa_sellprice_po/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('alphonsa_sellprice_po.listing', {
#             'root': '/alphonsa_sellprice_po/alphonsa_sellprice_po',
#             'objects': http.request.env['alphonsa_sellprice_po.alphonsa_sellprice_po'].search([]),
#         })

#     @http.route('/alphonsa_sellprice_po/alphonsa_sellprice_po/objects/<model("alphonsa_sellprice_po.alphonsa_sellprice_po"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alphonsa_sellprice_po.object', {
#             'object': obj
#         })