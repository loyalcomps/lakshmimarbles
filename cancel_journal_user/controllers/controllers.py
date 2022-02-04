# -*- coding: utf-8 -*-
from odoo import http

# class CancelJournalUser(http.Controller):
#     @http.route('/cancel_journal_user/cancel_journal_user/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cancel_journal_user/cancel_journal_user/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cancel_journal_user.listing', {
#             'root': '/cancel_journal_user/cancel_journal_user',
#             'objects': http.request.env['cancel_journal_user.cancel_journal_user'].search([]),
#         })

#     @http.route('/cancel_journal_user/cancel_journal_user/objects/<model("cancel_journal_user.cancel_journal_user"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cancel_journal_user.object', {
#             'object': obj
#         })