# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

import logging
log = logging.getLogger(__name__)


''' Purchase Order '''
class GST_PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_type = fields.Selection([
                        ('credit','Credit'),
                        ('cash','Cash')
                        ], default = 'credit', string="Purchase Type")
    reverse_charge = fields.Boolean(string="Reverse Charge Applicable?")

    place_of_supply = fields.Many2one('texbyte_gst.gstpos',string="Place of Supply",default=lambda self: self.company_id.place_of_supply or self.env.user.company_id.place_of_supply)


    """ Set place of supply based on vendor's GSTIN/address """
    @api.onchange('partner_id')
    def _set_sale_place_of_supply(self):
        if not self.partner_id:
            return
        pos_domain = []
        if self.partner_id.vat:
            pos_domain.append(('poscode', '=', self.partner_id.vat[0:2]))
        elif self.partner_id.state_id:
            pos_domain.append(('state_id', '=', self.partner_id.state_id.id))
        #if len(pos_domain) == 2:
        #    pos_domain = [|, pos_domain[0], pos_domain[1]]
        if not pos_domain:
            return

        self.place_of_supply = self.env['texbyte_gst.gstpos'].search(pos_domain, limit=1) or self.place_of_supply
        self._set_inter_state_tax()


    """ Change GST tax to IGST if place of supply of vendor is different from company's """
    @api.onchange('place_of_supply')
    def _set_inter_state_tax(self):
        company_id = self.company_id or self.env.user.company_id
        if self.place_of_supply and company_id.place_of_supply != self.place_of_supply:     #Apply IGST
            prod_no_hsn = ""
            fpos = self.fiscal_position_id or self.partner_id.property_account_position_id
            for line in self.order_line:
                if line.product_id.hsncode:
                    substitute_gst = fpos.map_tax(line.product_id.hsncode.gst_tax_ids.\
                                    filtered(lambda r: r.type_tax_use == 'purchase' and r.gst_type == 'igst').\
                                    filtered(lambda r: not line.company_id or r.company_id == company_id))
                    non_gst_taxes = line.taxes_id.filtered(lambda r: 'gst' not in r.gst_type).mapped('id')
                    line.taxes_id = self.env['account.tax'].browse([substitute_gst.id] + non_gst_taxes)    #Keep non-gst (CESS etc)
                else:
                    prod_no_hsn += line.product_id.name + ', '  #Collect the products for warning

        elif self.place_of_supply and self.place_of_supply.state_id.union_territory:        #Apply UGST
            prod_no_hsn = ""
            fpos = self.fiscal_position_id or self.partner_id.property_account_position_id
            for line in self.order_line:
                if line.product_id.hsncode:
                    substitute_gst = fpos.map_tax(line.product_id.hsncode.gst_tax_ids.\
                                    filtered(lambda r: r.type_tax_use == 'purchase' and r.gst_type == 'ugst').\
                                    filtered(lambda r: not line.company_id or r.company_id == company_id))
                    non_gst_taxes = line.taxes_id.filtered(lambda r: 'gst' not in r.gst_type).mapped('id')
                    line.taxes_id = self.env['account.tax'].browse([substitute_gst.id] + non_gst_taxes)    #Keep non-gst (CESS etc)
                else:
                    prod_no_hsn += line.product_id.name + ', '  #Collect the products for warning

        else:                                                                               #Apply GST
            prod_no_hsn = ""
            fpos = self.fiscal_position_id or self.partner_id.property_account_position_id
            for line in self.order_line:
                if line.product_id.hsncode:
                    substitute_gst = fpos.map_tax(line.product_id.hsncode.gst_tax_ids.\
                                    filtered(lambda r: r.type_tax_use == 'purchase' and r.gst_type == 'gst').\
                                    filtered(lambda r: not line.company_id or r.company_id == company_id))
                    non_gst_taxes = line.taxes_id.filtered(lambda r: 'gst' not in r.gst_type).mapped('id')
                    line.taxes_id = self.env['account.tax'].browse([substitute_gst.id] + non_gst_taxes)    #Keep non-gst (CESS etc)
                else:
                    prod_no_hsn += line.product_id.name + ', '  #Collect the products for warning

        if prod_no_hsn:
            warning_mess = {
                    'title': _('No HSN/SAC code'),
                    'message': _('No HSN code set for product(s) ' + prod_no_hsn + ' change the Tax to GST/IGST manually.')
                    }
            return {'warning': warning_mess}


    def _action_create_invoice_line(self, line=False, invoice_id=False):
        InvoiceLine = self.env['account.invoice.line']
        inv_name = line.product_id.name_get()[0][1]


''' Purchase Order Line '''
class GST_PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    ''' Warn when GST/IGST switch for product without HSN code happens '''
    @api.onchange('product_id')
    def _check_product_hsncode(self):
        if self.product_id and not self.product_id.hsncode and self.order_id.place_of_supply and self.order_id.place_of_supply != self.company_id.place_of_supply:
            warning_mess = {
                    'title': _('No HSN/SAC code'),
                    'message': _('No HSN code set for product %s, change the Tax to GST/IGST manually.') % (self.product_id.name)
                    }
            return {'warning': warning_mess}
        return {}


    ''' Switch tax to GST/IGST if place of supply differs '''
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super(GST_PurchaseOrderLine, self).onchange_product_id()

        #When buying from unregistered vendors, Reverse Charge applies (if daily expense exceeds 5000).
        #In that case, tax should not be applied, instead we will generate tax 'payable' (reverse charge) at end of the day from wizard
        if not self.order_id.partner_id.vat:
            self.taxes_id = []
            self._suggest_quantity()
            self._onchange_quantity()
            log.info("Unregistered vendor: PO taxes_id removed:" + str(self.taxes_id))

        if not self.taxes_id:   #Adding a new line on confirmed PO can result in tax not yet being populated...
            return result
        # Recompute taxes
        company_id = self.company_id or self.env.user.company_id
        if self.order_id.place_of_supply and company_id.place_of_supply != self.order_id.place_of_supply and self.product_id.hsncode:   #Apply IGST
            fpos = self.order_id.fiscal_position_id
            substitute_gst = fpos.map_tax(self.product_id.hsncode.gst_tax_ids.\
                            filtered(lambda r: r.type_tax_use == 'purchase' and r.gst_type == 'igst').\
                            filtered(lambda r: not self.company_id or r.company_id == company_id))
            non_gst_taxes = self.taxes_id.filtered(lambda r: 'gst' not in r.gst_type).mapped('id')
            tax_ids = self.env['account.tax'].browse([substitute_gst.id] + non_gst_taxes)    #Keep non-gst (CESS etc)
            if tax_ids:
                self.taxes_id = tax_ids
            self._suggest_quantity()
            self._onchange_quantity()

        elif self.order_id.place_of_supply and self.order_id.place_of_supply.state_id.union_territory and self.product_id.hsncode:      #Apply UGST
            fpos = self.order_id.fiscal_position_id
            substitute_gst = fpos.map_tax(self.product_id.hsncode.gst_tax_ids.\
                            filtered(lambda r: r.type_tax_use == 'purchase' and r.gst_type == 'ugst').\
                            filtered(lambda r: not self.company_id or r.company_id == company_id))
            non_gst_taxes = self.taxes_id.filtered(lambda r: 'gst' not in r.gst_type).mapped('id')
            tax_ids = self.env['account.tax'].browse([substitute_gst.id] + non_gst_taxes)    #Keep non-gst (CESS etc)
            if tax_ids:
                self.taxes_id = tax_ids
            self._suggest_quantity()
            self._onchange_quantity()

        return result
