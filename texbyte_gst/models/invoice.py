# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.tools import amount_to_text_en, float_round, float_compare
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import ValidationError

import math
import logging
log = logging.getLogger(__name__)

''' Account Invoice '''
class GST_Invoice(models.Model):
    _inherit = 'account.invoice'

    inv_trade_type = fields.Selection(string="Trade Type",
                        selection=[('cash','Cash'),('credit','Credit')], default='credit')

    place_of_supply = fields.Many2one('texbyte_gst.gstpos',string="Place of Supply",default=lambda self: self.company_id.place_of_supply or self.env.user.company_id.place_of_supply)
    reverse_charge = fields.Boolean(string="Reverse Charge Applicable?")
    transport_mode = fields.Selection([('road','Road'), ('rail','Rail'), ('air','Air'), ('other','Other')], string="Transport Mode")
    vehicle_no = fields.Char(string="Vehicle Number")



    @api.onchange('amount_total')
    def _onchange_amount(self):
        if hasattr(super(GST_Invoice, self), '_onchange_amount'):
            super(AccountRegisterPayments, self)._onchange_amount()
        # TODO: merge, refactor and complete the amount_to_text and amount_to_text_en classes
        for inv in self:
            amount_in_words = amount_to_text_en.amount_to_text(math.floor(inv.amount_total), lang='en', currency='')
            decimals = inv.amount_total % 1
            if decimals >= 10**-2:
                #TODO: Fix the hard coded currency name
                amount_in_words += " and " + amount_to_text_en.amount_to_text(int(round(float_round(decimals*100, precision_rounding=1))), lang='en', currency='') + " Paise"
            amount_in_words = amount_in_words.replace(' and Zero Cent', '') # Ugh
            inv.amount_in_words = amount_in_words

    # Field for amount in words
    amount_in_words = fields.Char(string="Amount in words", readonly=True, compute=_onchange_amount)


    ''' Set the Place of Supply from Purchase Order '''
    @api.onchange('purchase_id')
    def purchase_order_change(self):

        if not self.purchase_id:
            return {}
        # Set the field before calling superclass method as it also runs calculations based on field values
        self.place_of_supply = self.purchase_id.place_of_supply
        self.reverse_charge = self.purchase_id.reverse_charge

        # Set all the Invoice lines from PO lines  and run calculations
        return super(GST_Invoice,self).purchase_order_change()


    ''' Set/remove taxes when partner changes (for unregistered vendors). (There's already a method in super class)'''
    @api.onchange('partner_id')
    def _onchange_gst_partnerid(self):
        #Remove/set the taxes if necessary (only for Vendor Bills for now)
        if self.type in ('in_invoice','in_refund'):
            for line in self.invoice_line_ids:
                line._set_taxes()


    """ Set place of supply based on partner's GSTIN/address """
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


    #Change GST tax to IGST if place of supply of customer is different from company's
    @api.onchange('place_of_supply')
    def _set_inter_state_tax(self):
        prod_no_hsn = ""
        for line in self.invoice_line_ids:
            line._set_taxes()
            if not line.product_id.hsncode:
                prod_no_hsn += line.product_id.name + ', '  #Collect the products for warning

        if prod_no_hsn:
            warning_mess = {
                    'title': _('No HSN/SAC code'),
                    'message': _('No HSN code set for product(s) ' + prod_no_hsn + ' change the Tax to GST/IGST manually.')
                    }
            return {'warning': warning_mess}

    #Add a roundoff amount when confirming the Invoice
    @api.multi
    def action_invoice_open(self):
        self.add_roundoff()

        return super(GST_Invoice, self).action_invoice_open()

    #Add roundoff amount line
    @api.one
    def add_roundoff(self):
        #Check the settings if automatic roundoff adding is enabled
        company_id = self.company_id or self.env.user.company_id
        if company_id.add_roundoff == False:
            return

        #precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        #0. Calculate the round off adjustment (either round up or round down)
        decimal = self.amount_total % 1
        if float_is_zero(decimal, precision_digits=2):
            return

        roundoff_amt = 0.0
        roundoff_product = None
        if float_compare(decimal, 0.50, precision_digits=2) >= 0:   #Decimal part is >= 0.50, lets round up, product 'CHARGES'
            roundoff_amt = 1.0 - decimal
            roundoff_product = self.env['product.product'].search([('default_code', '=', 'CHARGES')], limit=1)
            roundoff_name = 'Roundoff(+)'
        else:       #Round down, product should be 'DISCOUNT' with value -ve
            roundoff_amt = 0.0 - decimal
            roundoff_product = self.env['product.product'].search([('default_code', '=', 'DISCOUNT')], limit=1)
            roundoff_name = 'Roundoff(-)'

        #1. Get the account id
        if self.type in ('out_invoice', 'out_refund'):
            roundoff_acc_id = roundoff_product.property_account_income_id.id or self.invoice_line_ids[0].with_context(journal_id=self.journal_id.id)._default_account()
        else:
            roundoff_acc_id = roundoff_product.property_account_expense_id.id or self.invoice_line_ids[0].with_context(journal_id=self.journal_id.id)._default_account()

        #2. Add invoice line
        # See event_sale/tests/test_event_sale.py
        roundoff_invoice_line = [(0,0, {
                'name': roundoff_name,
                'origin': self.origin,
                'price_unit': roundoff_amt,
                'quantity': 1,
                'product_id': roundoff_product.id,
                'uom_id': self.env.ref('product.product_uom_unit').id,
                'invoice_id': self.id,
                'account_id': roundoff_acc_id,
            } )]
        #log.info(self.amount_total)
        #log.info(self.invoice_line_ids)
        self.invoice_line_ids = roundoff_invoice_line      #[(0,0,{vals})] will cause append automatically
        #log.info(self.invoice_line_ids)
        #self.order_line[-1].product_id_change()     #DON'T call this, it will reset unit price
        #log.info(self.amount_total)

    @api.model
    def get_reference_unit(self,product_uom_id):
        """ Get reference base unit for a specific unit. """
        val = ""
        base_uom = self.env['product.uom'].search([('uom_type', '=', 'reference'), ('category_id', '=',product_uom_id.category_id.id )], limit=1)
        if base_uom:
            val = base_uom.name
        return val


    @api.multi
    def action_invoice_cancel(self):
        if self.filtered(lambda inv: inv.state == 'cancel'):
            raise UserError(_("Invoice is already cancelled."))
        #NOTE: Ask confirmation -- this is done via the button itself
        return self.action_cancel()


    @api.multi
    def action_cancel(self):
        moves = self.env['account.move']
        for inv in self:
            if inv.move_id:
                inv_number = inv.move_id.name
                moves += inv.move_id
            if inv.payment_move_line_ids:
                #If Invoice is paid, we must:
                #(1) Unreconcile the payment
                #(2) Cancel & Delete the payment journal entry
                moves += inv.payment_move_line_ids.move_id    #These will be cancelled and unlinked later. TODO: take all move_ids?
                #Unrecocile!
                inv.payment_move_line_ids.remove_move_reconcile()

                #raise UserError(_('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))

        # First, set the invoices as cancelled and detach the move ids
        self.write({'state': 'cancel', 'move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        # Unlinking the moves remove the invoice number, retain it
        if inv_number:
            self.write({'number': inv_number})

        return True


    def _get_refund_copy_fields(self):
        #Copy additional fields needed when creating Refund
        return ['inv_trade_type','place_of_supply','reverse_charge','transport_mode','vehicle_no'] \
                + super(GST_Invoice,self)._get_refund_copy_fields()


''' Account Invoice Line '''
class GST_InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    _order = "invoice_id,id,sequence"


    ''' Warn when GST/IGST switch for product without HSN code happens '''
    @api.onchange('product_id')
    def _check_product_hsncode(self):
        #Get the company id. Creating customer invoice/vendor bills directly may not set it...
        company_id = self.company_id or self.env.user.company_id
        if self.product_id and not self.product_id.hsncode and self.invoice_id.place_of_supply and self.invoice_id.place_of_supply != company_id.place_of_supply:
            warning_mess = {
                    'title': _('No HSN/SAC code'),
                    'message': _('No HSN code set for product %s, change the Tax to GST/IGST manually.') % (self.product_id.name)
                    }
            return {'warning': warning_mess}
        return {}


    ''' Override _set_taxes method to include IGST '''
    def _set_taxes(self):
        """ Used in on_change to set taxes and price."""
        #Get the company id. Creating customer invoice/vendor bills directly may not set it...
        company_id = self.company_id or self.env.user.company_id
        if self.invoice_id.type in ('out_invoice', 'out_refund'):   #Customer Invoice
            #If Place of Supply differs, apply IGST
            if self.invoice_id.place_of_supply and self.invoice_id.place_of_supply != company_id.place_of_supply and self.product_id.hsncode:
                taxes = self.product_id.hsncode.gst_tax_ids.filtered(lambda r: r.type_tax_use == 'sale' and r.gst_type == 'igst')
            #If Place of Supply is a Union Territory, apply IGST
            elif self.invoice_id.place_of_supply and self.invoice_id.place_of_supply.state_id.union_territory and self.product_id.hsncode:
                taxes = self.product_id.hsncode.gst_tax_ids.filtered(lambda r: r.type_tax_use == 'sale' and r.gst_type == 'ugst')
            else:
                taxes = self.product_id.taxes_id or self.account_id.tax_ids

        else:   #Vendor Bill
            #When buying from unregistered vendors, Reverse Charge applies (if daily expense exceeds 5000).
            #In that case, tax should not be applied, instead we will generate tax 'payable' (reverse charge) at end of the day from wizard
            #NOTE: During reverse charge posting, we need to compute the tax, so check the flag before removing taxes
            if not self.invoice_id.partner_id.vat and not self.env.context.get('dont_remove_tax'):
                taxes= self.env['account.tax']  #Set empty tax (down there's a taxes.filtered, so we can't set to empty list [])
                #self.invoice_line_tax_ids = []
                log.info("Unregistered vendor: Vendor Bill invoice_line_tax_ids removed:")
                #return

            else:
                #If Place of Supply differs, apply IGST
                if self.invoice_id.place_of_supply and self.invoice_id.place_of_supply != company_id.place_of_supply and self.product_id.hsncode:
                    taxes = self.product_id.hsncode.gst_tax_ids.filtered(lambda r: r.type_tax_use == 'purchase' and r.gst_type == 'igst')
                #If Place of Supply is a Union Territory, apply IGST
                elif self.invoice_id.place_of_supply and self.invoice_id.place_of_supply.state_id.union_territory and self.product_id.hsncode:
                    taxes = self.product_id.hsncode.gst_tax_ids.filtered(lambda r: r.type_tax_use == 'purchase' and r.gst_type == 'ugst')
                else:
                    taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids

        #If 'Reverse Charge' is applicable on this Invoice (from PO), add the 'Tax Payables' (basically customer taxes)
        #NOTE: This doesn't work as it 'adds' taxes instead of crediting it, and hence it doesn't reduce the Creditors amount
        #if self.invoice_id.reverse_charge and self.invoice_id.type in ('in_invoice', 'in_refund'):
        #    taxes += self.product_id.taxes_id

        # Keep only taxes of the company
        taxes = taxes.filtered(lambda r: r.company_id == company_id)
        #Add back non-GST taxes
        non_gst_taxes =  self.invoice_line_tax_ids.filtered(lambda r: 'gst' not in r.gst_type)
        if non_gst_taxes:
            taxes = self.env['account.tax'].browse(taxes.ids + non_gst_taxes.ids)  #Very important to fill the Many2many field correctly
        #log.info(taxes)

        self.invoice_line_tax_ids = fp_taxes = self.invoice_id.fiscal_position_id.map_tax(taxes, self.product_id, self.invoice_id.partner_id)

        fix_price = self.env['account.tax']._fix_tax_included_price
        if self.invoice_id.type in ('in_invoice', 'in_refund'):
            prec = self.env['decimal.precision'].precision_get('Product Price')
            if not self.price_unit or float_compare(self.price_unit, self.product_id.standard_price, precision_digits=prec) == 0:
                self.price_unit = fix_price(self.product_id.standard_price, taxes, fp_taxes)
        else:
            self.price_unit = fix_price(self.product_id.lst_price, taxes, fp_taxes)
