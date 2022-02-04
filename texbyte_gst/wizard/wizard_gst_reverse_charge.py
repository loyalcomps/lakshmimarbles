# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import float_compare, float_is_zero

import logging
_logger = logging.getLogger(__name__)

DAILY_UNREG_PURCHASE_AMOUNT_LIMIT = 5000

class GST_ReverseChargeAdjustment(models.TransientModel):
    _name = 'texbyte_gst.gst.reversecharge.wizard'
    _description = 'Wizard for GST Reverse Charge Tax Adjustments'

    @api.multi
    def _get_default_journal(self):
        return self.env['account.journal'].search([('type', '=', 'general')], limit=1).id

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, default=_get_default_journal) #, domain=[('type', '=', 'general')])
    date = fields.Date(required=True, default=fields.Date.context_today)
    debit_account_id = fields.Many2one('account.account', string='Debit account', required=False, domain=[('deprecated', '=', False)])   #ReverseChargeReceivable
    credit_account_id = fields.Many2one('account.account', string='Credit account', required=False, domain=[('deprecated', '=', False)]) #ReverseChargePayaable
    amount = fields.Monetary(currency_field='company_currency_id', required=False)
    company_currency_id = fields.Many2one('res.currency', readonly=True, default=lambda self: self.env.user.company_id.currency_id)
    tax_id = fields.Many2one('account.tax', string='Adjustment Tax', ondelete='restrict', domain=[('type_tax_use', '=', 'none'), ('tax_adjustment', '=', True)], required=False)

    @api.multi
    def _create_move(self,tax_sum_group):

        move_lines = []
        for tax_sum_line in tax_sum_group.values():
            #_logger.info("tax_sum_line")
            #_logger.info(tax_sum_line)
            if float_is_zero(tax_sum_line['amount'], precision_digits=5):   #Skip 0 amount entries
                continue

            #TODO: Take the configured payable accounts instead of this hack (searching by name), better error handling
            receivable_name = str(self.env['account.account'].browse(tax_sum_line['account_id']).name).replace('Receivable','Reverse Charge Receivable')
            receivable_account = self.env['account.account'].search([('name','=',receivable_name)], limit=1).id
            payable_name = receivable_name.replace('Receivable','Payable')
            payable_account = self.env['account.account'].search([('name','=',payable_name)], limit=1).id
            #Sometimes if the reverse accounts couldn't be determined...
            if not (receivable_account and payable_account):
                continue

            debit_vals = {
                    'name': 'Reverse Charge Tax',
                    'debit': tax_sum_line['amount'],
                    'credit': 0.0,
                    'account_id': receivable_account
                    }
            credit_vals = {
                    'name': 'Reverse Charge Tax',
                    'debit': 0.0,
                    'credit': tax_sum_line['amount'],
                    'account_id': payable_account
                    }
            move_lines.append((0,0,debit_vals))
            move_lines.append((0,0,credit_vals))
            #_logger.info("move_lines")
            #_logger.info(move_lines)

        vals = {
            'journal_id': self.journal_id.id,
            'ref': 'Revese Charge Tax: ' + self.date,
            'date': self.date,
            'state': 'draft',
            'line_ids': move_lines #[(0, 0, debit_vals), (0, 0, credit_vals)]
        }
        #_logger.info("vals:")
        #_logger.info(vals)
        move = self.env['account.move'].create(vals)
        #move.post()    #Don't post, keep in draft to give user an option to edit in case
        return move.id

    @api.multi
    def create_move(self,tax_sum_group):
        #create the adjustment move
        move_id = self._create_move(tax_sum_group)
        #return an action showing the created move
        action = self.env.ref(self.env.context.get('action', 'account.action_move_line_form'))
        result = action.read()[0]
        result['views'] = [(False, 'form')]
        result['res_id'] = move_id
        return result


    """ Calculate the total tax payable as Reverse Charge (for purchase from unregistered vendors)
        Plan:
            1. Remove tax from PO (and hence Invoice) if vendor is unregistered (done in purchase module)
            2. If total purchase expense for the day exceeds Rs. 5000 (TODO: handle currency?), reverse charge should be paid
            3. Collect all Purchase Invoice lines and apply tax (to calculate the removed-taxes)
            4. Sum the tax amount per Account ID (ultimately, posting by Payable/Receivable a/c matters)
            5. Prepare the Credit line for each summed Debit line and get the corresponding Payable Account
            6. Post the account move
            """
    def calculate_total_reverse_charge(self):
        date1 = self.date + " 00:00:00"
        date2 = self.date + " 24:00:00"
        #Vendor Bills from unregistered vendors
        unreg_vendorbills = self.env['account.invoice'].search([('type','in',('in_invoice','in_refund')),('date_invoice','>=',date1),('date_invoice','<=',date2),('partner_id.vat','=',False)])
        #_logger.info("Purcase from unregistered:")
        #_logger.info(unreg_purchases)
        #total_amount_untaxed = sum (purchase.amount_untaxed for purchase in unreg_purchases)
        # Unregistered purchases do not have tax applied, let us calculate tax for each item
        total_po_amount = 0.0
        tax_grouped = []
        #for po_inv_line in unreg_purchases.mapped('invoice_ids').filtered(lambda r: r.state in ('open','paid')).mapped('invoice_line_ids'):    #Purchase Invoice lines, open/paid
        for po_inv in unreg_vendorbills.filtered(lambda r: r.state in ('open','paid')):    #Purchase Invoice, open/paid
            #TODO: handle credit notes (price_subtotal_signed)
            total_po_amount += po_inv.amount_untaxed

            new_inv = po_inv
            #_logger.info("PO Invoice:")
            #_logger.info(new_inv)

            for inv_line in new_inv.invoice_line_ids:   #.filtered(lambda l: l.product_id.default_code not in ('ADVANCE', 'DISCOUNT', 'CHARGES')):
                if not inv_line.invoice_line_tax_ids:
                    #Instruct not to remove taxes this time (by setting flag)!
                    inv_line.with_context(dont_remove_tax=True)._set_taxes()   #Add the taxes to calculate the split and amount
            ##Get the tax move lines

            #Get grouped taxes
            tax_grouped.append(new_inv.get_taxes_values())
            #_logger.info("tax_grouped:")
            #_logger.info(tax_grouped)

        _logger.info("Total PO amount:" + str(total_po_amount))
        if total_po_amount <= DAILY_UNREG_PURCHASE_AMOUNT_LIMIT:
            raise UserError(_("Total unregistered purchase does not exceed 5000, reverse charge not created"))
            return

        #Total purchase expense exceeds the limit
        #Set 'Reverse Charge Applicable' flag on all the invoices
        for po_inv in unreg_vendorbills.filtered(lambda r:r.state in ('open','paid')):
            po_inv.reverse_charge = True    #TODO: could cause performance issue, use write?

        #Combine the tax entries by account
        tax_sum_per_group = {}
        for tax_grp in tax_grouped:
            #key = tax_grp.keys()[0]
            #_logger.info("tax_grouped key:" + str(key))
            for values in tax_grp.values():
                key = values['account_id']      #Group by account id
                if key not in tax_sum_per_group:
                    tax_sum_per_group[key] = values
                else:
                    tax_sum_per_group[key]['amount'] += values['amount']
                    tax_sum_per_group[key]['base'] += values['base']
        #_logger.info("tax_sum_per_group:")
        #_logger.info(tax_sum_per_group)

        #Create moves...
        return self.create_move(tax_sum_per_group)
