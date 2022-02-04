
from odoo import models, fields, api, _
from odoo.tools import amount_to_text_en, float_round, float_compare
from odoo.tools import float_is_zero, float_compare

class GST_Invoice(models.Model):
    _inherit = 'account.invoice'

    place_of_supply = fields.Many2one('gstr3b_report.gstpos', string="Place of Supply", default=lambda
        self: self.company_id.place_of_supply or self.env.user.company_id.place_of_supply)

    reverse_charge = fields.Boolean(string="Reverse Charge Applicable?")


    ''' Set the Place of Supply from Purchase Order '''

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        # Set the field before calling superclass method as it also runs calculations based on field values
        self.place_of_supply = self.purchase_id.place_of_supply
        self.reverse_charge = self.purchase_id.reverse_charge

        # Set all the Invoice lines from PO lines  and run calculations
        return super(GST_Invoice, self).purchase_order_change()

    @api.onchange('partner_id')
    def _set_sale_place_of_supply(self):
        if not self.partner_id:
            return
        pos_domain = []
        if self.partner_id.x_gstin:
            pos_domain.append(('poscode', '=', self.partner_id.x_gstin[0:2]))
        elif self.partner_id.state_id:
            pos_domain.append(('state_id', '=', self.partner_id.state_id.id))

        if not pos_domain:
            return

        self.place_of_supply = self.env['gstr3b_report.gstpos'].search(pos_domain, limit=1) or self.place_of_supply
        # self._set_inter_state_tax()

    def _get_refund_copy_fields(self):
        #Copy additional fields needed when creating Refund
        return ['place_of_supply','reverse_charge',] \
                + super(GST_Invoice,self)._get_refund_copy_fields()