# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import odoo
import json
import ast
import logging

_logger = logging.getLogger(__name__)




class pos_order_line(models.Model):
    _inherit = "pos.order.line"

    uom_id = fields.Many2one('product.uom', 'Uom', readonly=1)


