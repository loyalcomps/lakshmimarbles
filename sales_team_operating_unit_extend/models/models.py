# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        res = super(CrmTeam, self)._get_default_team_id(user_id)
        if not user_id:
            user_id = self.env.uid
        user = self.env['res.users'].search([('id','=',user_id)])
        team_id = self.env['crm.team'].search([('operating_unit_id','=',user.default_operating_unit_id.id)],limit=1)
        return team_id