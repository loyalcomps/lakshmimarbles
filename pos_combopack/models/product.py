from odoo import api, fields, models, _
import logging
from odoo.exceptions import UserError
import ast

_logger = logging.getLogger(__name__)

class product_template(models.Model):
    _inherit = 'product.template'

    pos_combo_item_ids = fields.One2many('pos.combo.pack', 'product_combo_id', string='Combo Packs')
    is_combo = fields.Boolean('Is combo')
    combo_limit = fields.Integer('Combo item limit', help='Limit combo packs can allow cashier add / combo')
    is_credit = fields.Boolean('Is credit', default=False)