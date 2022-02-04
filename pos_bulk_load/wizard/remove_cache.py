# -*- coding: utf-8 -*-

from odoo import api, fields, models
import json
import ast
import logging


_logger = logging.getLogger(__name__)

class pos_remove_cache(models.TransientModel):
    _name = 'pos.remove.cache'

    @api.multi
    def remove_cache(self):
        self.env['pos.cache.database'].search([]).unlink()
        modules = [
            'product.product',
            'res.partner',
            # 'account.invoice',
            # 'pos.order',
            # 'pos.order.line',
            # 'product.pricelist',
            # 'product.pricelist.item'
        ]
        for module in modules:
            params = self.env['ir.config_parameter'].sudo().get_param(module)
            if params:
                _logger.info('{cached} %s' % module)
                params = ast.literal_eval(params)
                datas = self.env[module].search(params.get('domain', [])).with_context(params.get('context', {})).read(params.get('fields', []))
                for data in datas:
                    self.env.cr.execute("insert into pos_cache_database (res_id, res_model, data) VALUES (%s, %s, %s)",
                                        (data['id'], module, json.dumps(data),))
            else:
                _logger.error('{params} null')
        return True
