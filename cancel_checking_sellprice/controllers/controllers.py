# -*- coding: utf-8 -*-
from odoo import http

# class CancelCheckingSellprice(http.Controller):
#     @http.route('/cancel_checking_sellprice/cancel_checking_sellprice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cancel_checking_sellprice/cancel_checking_sellprice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cancel_checking_sellprice.listing', {
#             'root': '/cancel_checking_sellprice/cancel_checking_sellprice',
#             'objects': http.request.env['cancel_checking_sellprice.cancel_checking_sellprice'].search([]),
#         })

#     @http.route('/cancel_checking_sellprice/cancel_checking_sellprice/objects/<model("cancel_checking_sellprice.cancel_checking_sellprice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cancel_checking_sellprice.object', {
#             'object': obj
#         })