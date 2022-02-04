# -*- coding: utf-8 -*-
from odoo import http

# class ProductArticleNo(http.Controller):
#     @http.route('/product_article_no/product_article_no/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_article_no/product_article_no/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_article_no.listing', {
#             'root': '/product_article_no/product_article_no',
#             'objects': http.request.env['product_article_no.product_article_no'].search([]),
#         })

#     @http.route('/product_article_no/product_article_no/objects/<model("product_article_no.product_article_no"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_article_no.object', {
#             'object': obj
#         })