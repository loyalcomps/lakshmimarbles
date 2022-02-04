# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseArticleNo(http.Controller):
#     @http.route('/purchase_article_no/purchase_article_no/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_article_no/purchase_article_no/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_article_no.listing', {
#             'root': '/purchase_article_no/purchase_article_no',
#             'objects': http.request.env['purchase_article_no.purchase_article_no'].search([]),
#         })

#     @http.route('/purchase_article_no/purchase_article_no/objects/<model("purchase_article_no.purchase_article_no"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_article_no.object', {
#             'object': obj
#         })