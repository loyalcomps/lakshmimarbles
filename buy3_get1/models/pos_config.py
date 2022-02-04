# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import ast
import logging
from odoo.exceptions import UserError
import base64
import json

import io
import os
import timeit

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

_logger = logging.getLogger(__name__)

class pos_config(models.Model):
    _inherit = "pos.config"

    promotion_ids = fields.Many2many('pos.promotion',
                                     'pos_config_promotion_rel',
                                     'config_id',
                                     'promotion_id',
                                     string='Promotion programs')

    promotion_manual_select = fields.Boolean(string='Promotion Manual Choice',default=True)
