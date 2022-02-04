# -*- coding: utf-8 -*-
from odoo import http

# class InclusiveJournalCosting(http.Controller):
#     @http.route('/inclusive_journal_costing/inclusive_journal_costing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inclusive_journal_costing/inclusive_journal_costing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inclusive_journal_costing.listing', {
#             'root': '/inclusive_journal_costing/inclusive_journal_costing',
#             'objects': http.request.env['inclusive_journal_costing.inclusive_journal_costing'].search([]),
#         })

#     @http.route('/inclusive_journal_costing/inclusive_journal_costing/objects/<model("inclusive_journal_costing.inclusive_journal_costing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inclusive_journal_costing.object', {
#             'object': obj
#         })