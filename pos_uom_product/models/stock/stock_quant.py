# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
import odoo
_logger = logging.getLogger(__name__)

class stock_quant(models.Model):

    _inherit = "stock.quant"

    def get_current_qty_available(self, product_id, stock_location_id):
        qty_available = 0
        version_info = odoo.release.version_info
        quants = self.search([('product_id', '=', product_id), ('location_id', '=', stock_location_id)])
        for quant in quants:
            if version_info and version_info[0] == 11:
                qty_available += quant.quantity
            if version_info and version_info[0] == 10:
                qty_available += quant.qty
        return {
            'stock_location_id': stock_location_id,
            'qty_available': qty_available,
        }

    @api.model
    def create(self, vals):
        res = super(stock_quant, self).create(vals)
        self.sync_pos(vals['product_id'])
        return res

    @api.multi
    def write(self, vals):
        res = super(stock_quant, self).write(vals)
        for record in self:
            self.sync_pos(record.product_id.id)
        return res

    def sync_pos(self, product_id):
        sql = "select stock_location_id from pos_config"
        self.env.cr.execute(sql)
        stock_location_ids = self.env.cr.fetchall()
        stock_datas = {
            'product_id': product_id,
            'stock_datas': []
        }
        for stock_location_id in stock_location_ids:
            stock_datas['stock_datas'].append(self.get_current_qty_available(product_id, stock_location_id[0]))

        _logger.info('send notification update stock')
        sessions = self.env['pos.session'].sudo().search([
            ('state', '=', 'opened'),
        ])
        for session in sessions:
            _logger.info('sync qty on hand to: %s' % session.user_id.login)
            _logger.info('{0}'.format(stock_datas))
            notifications = [[(self._cr.dbname, 'pos.stock.update', session.user_id.id), stock_datas]]
            self.env['bus.bus'].sendmany(notifications)
        return True
