# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
from odoo.exceptions import UserError
import ast

_logger = logging.getLogger(__name__)

class product_template(models.Model):
    _inherit = 'product.template'

    # @api.multi
    # def write(self, vals):
    #     res = super(product_template, self).write(vals)

    #     for product_temp in self:
    #         products = self.env['product.product'].search([('product_tmpl_id', '=', product_temp.id)])
    #         for product in products:
    #             if product.sale_ok and product.available_in_pos:
    #                 product.sync_data()
    #     return res


class product_product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def write(self, vals):
        res = super(product_product, self).write(vals)
        for product in self:
            if product.sale_ok and product.available_in_pos:
                product.sync_data()
        return res

    def sync_data(self):
        datas = self.get_data()
        sessions = self.env['pos.session'].sudo().search([
            ('state', '=', 'opened')
        ])
        self.env['pos.cache.database'].add_cache_record(self)
        if datas:
            for session in sessions:
                _logger.info('{sync_data} to session ID %s' % session.id)
                self.env['bus.bus'].sendmany(
                    [[(self.env.cr.dbname, 'pos.sync.data', session.user_id.id), datas]])

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
        product = super(product_product, self).create(vals)
        if product.sale_ok and product.available_in_pos:
            product.sync_data()
        return product

    @api.multi
    def unlink(self):
        for record in self:
            self.env['pos.cache.database'].remove_cache_record(record)
        return super(product_product, self).unlink()

