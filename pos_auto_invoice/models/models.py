# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)
class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create_from_ui(self, orders):

        _logger.info('begin invoice create_from_ui')

        order_ids = super(PosOrder, self).create_from_ui(orders)

        orders_object = self.browse(order_ids)

        for order in orders_object:

            order.action_pos_order_invoice_direct()
            order.invoice_id.sudo().action_invoice_open()
            order.account_move = order.invoice_id.move_id


        _logger.info('end invoice create_from_ui')
        return order_ids

    @api.multi
    def action_pos_order_invoice_direct(self):
        Invoice = self.env['account.invoice']

        for order in self:
            # Force company for all SUPERUSER_ID action
            local_context = dict(self.env.context, force_company=order.company_id.id, company_id=order.company_id.id)
            if order.invoice_id:
                Invoice += order.invoice_id
                continue
            # partner = self.env['res.partner'].search([('name','=','CASH')], limit=1)

            # if partner:
            #     order.partner_id = partner.id

            if not order.partner_id:

                partner = self.env['res.partner'].search([('name','=','CASH')], limit=1)

                if partner:
                    order.partner_id = partner.id

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            invoice = Invoice.new(order._prepare_invoice_direct())
            invoice._onchange_partner_id()
            invoice.fiscal_position_id = order.fiscal_position_id

            inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
            new_invoice = Invoice.with_context(local_context).sudo().create(inv)
            message = _(
                "This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (
                      order.id, order.name)
            new_invoice.message_post(body=message)
            order.write({'invoice_id': new_invoice.id, 'state': 'invoiced'})
            Invoice += new_invoice

            for line in order.lines:
                self.with_context(local_context)._action_create_invoice_line(line, new_invoice.id)

            new_invoice.with_context(local_context).sudo().compute_taxes()
            order.sudo().write({'state': 'invoiced'})
            # this workflow signal didn't exist on account.invoice -> should it have been 'invoice_open' ? (and now method .action_invoice_open())
            # shouldn't the created invoice be marked as paid, seing the customer paid in the POS?
            # new_invoice.sudo().signal_workflow('validate')

        if not Invoice:
            return {}

    def _prepare_invoice_direct(self):
        """
        Prepare the dict of values to create the new invoice for a pos order.
        """
        return {
            'name': self.name,
            'origin': self.name,
            'account_id': self.partner_id.property_account_receivable_id.id,
            'journal_id': self.session_id.config_id.invoice_journal_id.id,
            'company_id': self.company_id.id,
            'type': 'out_invoice',
            'reference': self.name,
            'partner_id': self.partner_id.id,
            'comment': self.note or '',
            # considering partner's sale pricelist's currency
            'currency_id': self.pricelist_id.currency_id.id,
            'user_id': self.env.uid,
        }

