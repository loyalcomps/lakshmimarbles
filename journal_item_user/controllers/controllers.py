# -*- coding: utf-8 -*-
from odoo import http

# class JournalItemUser(http.Controller):
#     @http.route('/journal_item_user/journal_item_user/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/journal_item_user/journal_item_user/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('journal_item_user.listing', {
#             'root': '/journal_item_user/journal_item_user',
#             'objects': http.request.env['journal_item_user.journal_item_user'].search([]),
#         })

#     @http.route('/journal_item_user/journal_item_user/objects/<model("journal_item_user.journal_item_user"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('journal_item_user.object', {
#             'object': obj
#         })