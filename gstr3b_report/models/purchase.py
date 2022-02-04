
from odoo import models, fields, api, _

import logging
log = logging.getLogger(__name__)

class GST_PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    reverse_charge = fields.Boolean(string="Reverse Charge Applicable?")
    place_of_supply = fields.Many2one('gstr3b_report.gstpos', string="Place of Supply", default=lambda
        self: self.company_id.place_of_supply or self.env.user.company_id.place_of_supply)

    """ Set place of supply based on vendor's GSTIN/address """

    @api.onchange('partner_id')
    def _set_sale_place_of_supply(self):
        if not self.partner_id:
            return
        pos_domain = []
        if self.partner_id.vat:
            pos_domain.append(('poscode', '=', self.partner_id.x_gstin[0:2]))
        elif self.partner_id.state_id:
            pos_domain.append(('state_id', '=', self.partner_id.state_id.id))

        if not pos_domain:
            return

        self.place_of_supply = self.env['gstr3b_report.gstpos'].search(pos_domain, limit=1) or self.place_of_supply
        # self._set_inter_state_tax()


