# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking')
    stock_return = fields.Boolean(string="Stock return", compute="check_stock_return")

    @api.multi
    @api.depends("stock_picking_id")
    def check_stock_return(self):
        """Know if this invoice is a refund or not."""
        for one in self:
            if one.stock_picking_id:
                one.stock_return = True

    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search(
            [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search(
                [('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return types[:1]

    @api.model
    def _default_picking_type_purchase(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search(
            [('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search(
                [('code', '=', 'outgoing'), ('warehouse_id', '=', False)])
        return types[:1]

    @api.multi
    def _get_destination_location(self):
        type_obj = self.env['stock.picking.type']

        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search(
            [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search(
                [('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        picking_type_id = types[:1]
        default_location_dest_id = picking_type_id.search(
            [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id),],
            limit=1).default_location_dest_id
        return default_location_dest_id

    @api.multi
    def _get_destination_location_purchase(self):
        type_obj = self.env['stock.picking.type']

        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search(
            [('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search(
                [('code', '=', 'outgoing'), ('warehouse_id', '=', False)])
        picking_type_id = types[:1]
        default_location_dest_id = picking_type_id.search(
            [('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)],
            limit=1).default_location_src_id
        return default_location_dest_id

    @api.model
    def _prepare_picking(self):

        if not self.partner_id.property_stock_customer.id:
            raise UserError(_("You must set a Customer Location for this partner %s") % self.partner_id.name)

        return {
            'picking_type_id': self._default_picking_type().id,
            'partner_id': self.partner_id.id,
            'date': self.date_invoice,
            'origin': self.name,
            'location_dest_id': self._get_destination_location().id,
            'location_id': self.partner_id.property_stock_customer.id,
            'company_id': self.company_id.id,
        }

    @api.model
    def _prepare_picking_purchase(self):

        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)

        return {
            'picking_type_id': self._default_picking_type_purchase().id,
            'partner_id': self.partner_id.id,
            'date': self.date_invoice,
            'origin': self.name,
            'location_dest_id': self.partner_id.property_stock_supplier.id,
            'location_id': self._get_destination_location_purchase().id,
            'company_id': self.company_id.id,
        }

    @api.multi
    def return_stock(self):

        for invoice in self:

            if any([ptype in ['product', 'consu'] for ptype in invoice.invoice_line_ids.mapped('product_id.type')]):
                res = invoice._prepare_picking()
                picking = self.env['stock.picking'].create(res)
                moves = invoice.invoice_line_ids.filtered(
                    lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(picking)
                move_ids = moves.action_confirm()
                # moves = self.env['stock.move'].browse(move_ids)
                move_ids.force_assign()
                invoice.stock_picking_id = picking.id
                stock_picking_obj = self.env['stock.picking'].browse(picking.id)
                for operation in stock_picking_obj.pack_operation_product_ids:
                    operation.write({'qty_done': operation.product_qty})

                return_res = picking.do_new_transfer()
                #                 invoice.stock_return = True

        return True

    @api.multi
    def return_stock_purchase(self):

        for invoice in self:

            if any([ptype in ['product', 'consu'] for ptype in invoice.invoice_line_ids.mapped('product_id.type')]):
                res = invoice._prepare_picking_purchase()
                picking = self.env['stock.picking'].create(res)
                moves = invoice.invoice_line_ids.filtered(
                    lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves_purchase(picking)
                move_ids = moves.filtered(lambda x: x.state not in ('done', 'cancel')).action_confirm()
                seq = 0
                for move in sorted(move_ids, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                # move_ids = moves.action_confirm()
                # moves = self.env['stock.move'].browse(move_ids)
                move_ids.force_assign()
                invoice.stock_picking_id = picking.id
                stock_picking_obj = self.env['stock.picking'].browse(picking.id)
                for operation in stock_picking_obj.pack_operation_product_ids:
                    operation.write({'qty_done': operation.product_qty})

                return_res = picking.do_new_transfer()
                #                 invoice.stock_return = True

        return True

    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        # override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}

        # choose the view_mode accordingly
        res = self.env.ref('stock.view_picking_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = self.stock_picking_id.id or False
        return result

class AccountInvoiceLine(models.Model):
    """ Override AccountInvoice_line to add the link to the sale order line it is related to"""
    _inherit = 'account.invoice.line'

    @api.multi
    def _get_stock_move_price_unit(self):
        self.ensure_one()
        line = self[0]
        order = line.invoice_id
        price_unit = line.price_unit
        if line.invoice_line_tax_ids:
            if line.invoice_id.inclusive:
                price_unit = line.invoice_line_tax_ids.with_context(round=False,price_include=True,
                                                               include_base_amount=True).compute_all_inc(price_unit,
                                                                                                         currency=line.invoice_id.currency_id,
                                                                                                         quantity=1.0,product=line.product_id, partner=line.invoice_id.partner_id)['total_excluded']
            else:
                price_unit = line.invoice_line_tax_ids.with_context(round=False).compute_all(price_unit, currency=line.invoice_id.currency_id, quantity=1.0,
                        product=line.product_id,partner=line.invoice_id.partner_id)['total_excluded']

        if line.uom_id.id != line.product_id.uom_id.id:
            price_unit *= line.uom_id.factor / line.product_id.uom_id.factor
        if order.currency_id != order.company_id.currency_id:
            price_unit = order.currency_id.compute(price_unit, order.company_id.currency_id, round=False)
        return price_unit

    @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            price_unit = line._get_stock_move_price_unit()

            template = {
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.uom_id.id,
                'date': line.invoice_id.date_invoice or fields.Date.today(),
                'date_expected': line.invoice_id.date_invoice or fields.Date.today(),
                'location_id': line.invoice_id.partner_id.property_stock_customer.id,
                'location_dest_id': line.invoice_id._get_destination_location().id,
                'picking_id': picking.id,
                'partner_id': line.invoice_id.partner_id.id,
                'move_dest_id': False,
                'state': 'draft',
                'company_id': line.invoice_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': line.invoice_id._default_picking_type().id,
                'procurement_id': False,
                'origin': line.invoice_id.name,
                'warehouse_id': line.invoice_id._default_picking_type().warehouse_id.id,
                'product_uom_qty': line.quantity,
            }

            done += moves.create(template)
        return done

    @api.multi
    def _create_stock_moves_purchase(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            price_unit = line._get_stock_move_price_unit()

            template = {
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.uom_id.id,
                'date': line.invoice_id.date_invoice or fields.Date.today(),
                'date_expected': line.invoice_id.date_invoice or fields.Date.today(),
                'location_id': line.invoice_id._get_destination_location_purchase().id,
                'location_dest_id': line.invoice_id.partner_id.property_stock_supplier.id,
                'picking_id': picking.id,
                'partner_id': line.invoice_id.partner_id.id,
                'move_dest_id': False,
                'state': 'draft',
                #                 'purchase_line_id': line.id,
                'company_id': line.invoice_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': line.invoice_id._default_picking_type_purchase().id,
                #                 'group_id': line.invoice_id.group_id.id,
                'procurement_id': False,

                'origin': line.invoice_id.name,
                #                 'route_ids': line.invoice_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in line.order_id.picking_type_id.warehouse_id.route_ids])] or [],
                'warehouse_id': line.invoice_id._default_picking_type_purchase().warehouse_id.id,
                'product_uom_qty': line.quantity,
            }

            done += moves.create(template)
        return done