# -*- coding: utf-8 -*-

from odoo import api, fields, models
import json
import ast
import logging


_logger = logging.getLogger(__name__)

class pos_order_import(models.TransientModel):
    _name = 'pos.order.import'

    date_start = fields.Date('Date', required=True, default=fields.Date.context_today)
    date_end = fields.Date('Date End', required=True, default=fields.Date.context_today)

    @api.multi
    def import_order(self):

        date_start = self.date_start
        date_end = self.date_end
        company_id = self.env.user.company_id.id


        pos_orders = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                   ('company_id', '=', company_id),
                                                   ('state', 'in', ['paid','done'])
                                                   ],limit=100)

        _logger.info('begin pos to invoice')

        for order in pos_orders:
            order.action_pos_order_invoice_direct()
            order.invoice_id.sudo().action_invoice_open()
            order.account_move = order.invoice_id.move_id

        _logger.info('end pos to invoice')

        return True

