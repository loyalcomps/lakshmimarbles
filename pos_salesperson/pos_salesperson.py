import odoo
from odoo import models,fields, api

from odoo.tools.translate import _
import time
import logging
_logger = logging.getLogger(__name__)


class pos_order(models.Model):
    _inherit = 'pos.order'
    _name='pos.order'



    salesperson_name = fields.Char(string='salesperson')


    def _order_fields(self,order):
        fields = super(pos_order, self)._order_fields(order)
        fields['salesperson_name'] = order.get('salesperson_name')
        return fields
