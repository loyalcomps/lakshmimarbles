# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, _


_logger = logging.getLogger(__name__)


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    product_mrp = fields.Float(string='MRP', digits=0)