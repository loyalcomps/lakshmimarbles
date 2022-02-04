# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

import logging
log = logging.getLogger(__name__)


''' Sale Order '''
class GST_SaleOrder(models.Model):
    _inherit = 'sale.order'

    place_of_supply = fields.Many2one('gstr3b_report.gstpos',string="Place of Supply",default=lambda self: self.company_id.place_of_supply or self.env.user.company_id.place_of_supply)
    # transport_mode = fields.Selection([('road','Road'), ('rail','Rail'), ('air','Air'), ('other','Other')], string="Transport Mode")
    # vehicle_no = fields.Char(string="Vehicle Number")

    #Set the sale_type automatically based on menu chosen by user
    # sale_type = fields.Selection(string="Sale Type", selection=[('cash','Cash'),('credit','Credit')], default='credit')


    # """ Indicate whether all deliveries are done or not """
    # @api.depends('picking_ids', 'picking_ids.state')
    # def _compute_is_shipped(self):
    #     for order in self:
    #         if order.picking_ids and all([x.state == 'done' for x in order.picking_ids]):
    #             order.is_shipped = True
    #
    # is_shipped = fields.Boolean(compute="_compute_is_shipped")

    #---------------------------------------------------------------------

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        # Call the superclass method which fills standard fields
        invoice_vals = super(GST_SaleOrder,self)._prepare_invoice()

        #Set custom fields added by us
        # invoice_vals['inv_trade_type']  = self.sale_type
        invoice_vals['place_of_supply'] = self.place_of_supply.id
        # invoice_vals['transport_mode']  = self.transport_mode
        # invoice_vals['vehicle_no']      = self.vehicle_no

        return invoice_vals

    """ Set place of supply based on customer's GSTIN/shipping address """
    @api.onchange('partner_shipping_id')
    def _set_sale_place_of_supply(self):
        if not self.partner_shipping_id:
            return
        pos_domain = []
        if self.partner_id.x_gstin:
            pos_domain.append(('poscode', '=', self.partner_id.x_gstin[0:2]))
        elif self.partner_shipping_id.state_id:
            pos_domain.append(('state_id', '=', self.partner_shipping_id.state_id.id))
        #if len(pos_domain) == 2:
        #    pos_domain = [|, pos_domain[0], pos_domain[1]]
        if not pos_domain:
            return

        self.place_of_supply = self.env['gstr3b_report.gstpos'].search(pos_domain, limit=1) or self.place_of_supply
        # self._set_inter_state_tax()


    #Change GST tax to IGST if place of supply of customer is different from company's
    # @api.onchange('place_of_supply')
    # def _set_inter_state_tax(self):
    #     company_id = self.company_id or self.env.user.company_id
    #     if self.place_of_supply and company_id.place_of_supply != self.place_of_supply:
    #         prod_no_hsn = ""
    #         fpos = self.fiscal_position_id or self.partner_id.property_account_position_id
    #         for line in self.order_line:
    #             if line.product_id.hsncode:
    #                 company_id = line.company_id or company_id
    #                 taxes = line.product_id.hsncode.gst_tax_ids.\
    #                         filtered(lambda r: r.type_tax_use == 'sale' and r.gst_type == 'igst').\
    #                         filtered(lambda r: not company_id or r.company_id == company_id)
    #                 substitute_gst = fpos.map_tax(taxes, line.product_id, line.order_id.partner_id) if fpos else taxes
    #                 non_gst_taxes = line.tax_id.filtered(lambda r: 'gst' not in r.gst_type).mapped('id')
    #                 line.tax_id = self.env['account.tax'].browse([substitute_gst.id] + non_gst_taxes)    #Keep non-gst (CESS etc)
    #             else:
    #                 prod_no_hsn += line.product_id.name + ', '  #Collect the products for warning
    #
    #         if prod_no_hsn:
    #             warning_mess = {
    #                     'title': _('No HSN/SAC code'),
    #                     'message': _('No HSN code set for product(s) ' + prod_no_hsn + ' change the Tax to GST/IGST manually.')
    #                     }
    #             return {'warning': warning_mess}
    #
    #     else:
    #         super(GST_SaleOrder,self)._compute_tax_id()


''' Sale Order Line '''
class GST_SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    #
    # ''' Warn when GST/IGST switch for product without HSN code happens '''
    # @api.onchange('product_id')
    # def _check_product_hsncode(self):
    #     company_id = self.company_id or self.env.user.company_id
    #     if self.product_id and not self.product_id.hsncode and self.order_id.place_of_supply and self.order_id.place_of_supply != company_id.place_of_supply:
    #         warning_mess = {
    #                 'title': _('No HSN/SAC code'),
    #                 'message': _('No HSN code set for product %s, change the Tax to GST/IGST manually.') % (self.product_id.name)
    #                 }
    #         return {'warning': warning_mess}
    #     return {}
    #
    # ''' Overload the _compute_tax_id to set IGST in case Place of Supply differ '''
    # @api.multi
    # def _compute_tax_id(self):
    #     for line in self:
    #         company_id = line.company_id or self.env.user.company_id
    #         # If Place of Supply differs, apply IGST
    #         if line.order_id.place_of_supply and line.order_id.place_of_supply != company_id.place_of_supply and line.product_id.hsncode:
    #             fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
    #             taxes = line.product_id.hsncode.gst_tax_ids.\
    #                     filtered(lambda r: r.type_tax_use == 'sale' and r.gst_type == 'igst').\
    #                     filtered(lambda r: not line.company_id or r.company_id == line.company_id)
    #             substitute_gst = fpos.map_tax(taxes, line.product_id, line.order_id.partner_id) if fpos else taxes
    #             non_gst_taxes = line.tax_id.filtered(lambda r: 'gst' not in r.gst_type).mapped('id')
    #             line.tax_id = self.env['account.tax'].browse([substitute_gst.id] + non_gst_taxes)    #Keep non-gst (CESS etc)
    #         # If Place of Supply is a Union Territory, apply UGST(CSGT+UTGST)
    #         elif line.order_id.place_of_supply and line.order_id.place_of_supply.state_id.union_territory and line.product_id.hsncode:
    #             fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
    #             taxes = line.product_id.hsncode.gst_tax_ids.\
    #                     filtered(lambda r: r.type_tax_use == 'sale' and r.gst_type == 'ugst').\
    #                     filtered(lambda r: not line.company_id or r.company_id == line.company_id)
    #             substitute_gst = fpos.map_tax(taxes, line.product_id, line.order_id.partner_id) if fpos else taxes
    #             non_gst_taxes = line.tax_id.filtered(lambda r: 'gst' not in r.gst_type).mapped('id')
    #             line.tax_id = self.env['account.tax'].browse([substitute_gst.id] + non_gst_taxes)    #Keep non-gst (CESS etc)
    #         #Otherwise, apply usual tax calculation
    #         else:
    #             super(GST_SaleOrderLine,self)._compute_tax_id()
