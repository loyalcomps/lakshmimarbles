# -*- coding: utf-8 -*-
from odoo import http

# class SalesTeamOperatingUnitExtend(http.Controller):
#     @http.route('/sales_team_operating_unit_extend/sales_team_operating_unit_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_team_operating_unit_extend/sales_team_operating_unit_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_team_operating_unit_extend.listing', {
#             'root': '/sales_team_operating_unit_extend/sales_team_operating_unit_extend',
#             'objects': http.request.env['sales_team_operating_unit_extend.sales_team_operating_unit_extend'].search([]),
#         })

#     @http.route('/sales_team_operating_unit_extend/sales_team_operating_unit_extend/objects/<model("sales_team_operating_unit_extend.sales_team_operating_unit_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_team_operating_unit_extend.object', {
#             'object': obj
#         })