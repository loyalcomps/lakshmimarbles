# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
import ast
_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = "res.partner"


    def sync_data(self):
        datas = self.get_data()

        self.env['pos.cache.database'].add_cache_record(self)


    def get_data(self):
        params = self.env['ir.config_parameter'].sudo().get_param(self._name)
        if params:
            params = ast.literal_eval(params)
            datas = self.with_context(params.get('context', {})).read(params.get('fields', []))[0]
            datas['model'] = self._name
            return datas
        else:
            return None

    @api.model
    def create(self, vals):
        partner = super(res_partner, self).create(vals)
        if partner.customer:

            partner.sync_data()
        return partner

    @api.multi
    def write(self, vals):
        res = super(res_partner, self).write(vals)
        for partner in self:
            if partner.customer:
                partner.sync_data()
        return res

    @api.multi
    def unlink(self):
        for record in self:
            self.env['pos.cache.database'].remove_cache_record(record)
        return super(res_partner, self).unlink()