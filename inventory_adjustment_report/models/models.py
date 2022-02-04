# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, _


_logger = logging.getLogger(__name__)


class stock_inventory_val(models.Model):
    _inherit = 'stock.inventory.line'

    cost_price_val = fields.Float('cost',related='product_id.standard_price',store=True)
    # date_expected = fields.Date()
    # product_uom = fields.Float()



    # @api.multi
    # @api.onchange('product_id')
    # def cost_updation_inventory(self):
    #     for inventory in self:
    #         inventory.cost_price_val = inventory.product_id.standard_price