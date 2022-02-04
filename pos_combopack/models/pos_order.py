# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
import logging
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import json

_logger = logging.getLogger(__name__)

class pos_order(models.Model):
    _inherit = "pos.order"


    @api.model
    def create_from_ui(self, orders):
        _logger.info('begin create_from_ui')

        order_ids = super(pos_order, self).create_from_ui(orders)
        # _logger.info(order_ids)
        orders_object = self.browse(order_ids)

        for order in orders_object:

            # combo
            for o in orders:
                StockWarehouse = self.env['stock.warehouse']
                Move = self.env['stock.move']
                moves = Move
                Picking = self.env['stock.picking']
                Product = self.env['product.product']
                if o['data']['name'] == order.pos_reference:
                    combo_items = []
                    picking_type = order.picking_type_id
                    location_id = order.location_id.id
                    address = order.partner_id.address_get(['delivery']) or {}
                    if order.partner_id:
                        destination_id = order.partner_id.property_stock_customer.id
                    else:
                        if (not picking_type) or (not picking_type.default_location_dest_id):
                            customerloc, supplierloc = StockWarehouse._get_partner_locations()
                            destination_id = customerloc.id
                        else:
                            destination_id = picking_type.default_location_dest_id.id
                    if o['data'] and o['data'].get('lines', False):
                        for line in o['data']['lines']:
                            if line[2] and line[2].get('combo_items', False):
                                for item in line[2]['combo_items']:
                                    combo_items.append(item)
                                del line[2]['combo_items']
                    if combo_items:
                        _logger.info('Processing Order have combo lines')
                        picking_vals = {
                            'name': order.name + '/Combo',
                            'origin': order.name,
                            'partner_id': address.get('delivery', False),
                            'date_done': order.date_order,
                            'picking_type_id': picking_type.id,
                            'company_id': order.company_id.id,
                            'move_type': 'direct',
                            'note': order.note or "",
                            'location_id': location_id,
                            'location_dest_id': destination_id,
                            'pos_order_id': order.id,
                        }
                        _logger.info('{0}'.format(picking_vals))
                        order_picking = Picking.sudo().create(picking_vals)
                        for item in combo_items:
                            product = Product.browse(item['product_id'][0])
                            moves |= Move.sudo().create({
                                'name': order.name,
                                'product_uom': product.uom_id.id,
                                'picking_id': order_picking.id,
                                'picking_type_id': picking_type.id,
                                'product_id': product.id,
                                'product_uom_qty': abs(item['quantity']),
                                'state': 'draft',
                                'location_id': location_id,
                                'location_dest_id': destination_id,
                            })

                        order.sudo()._force_picking_done(order_picking)
                        _logger.info('Delivery combo: %s' % order_picking.name)
        _logger.info('end create_from_ui')
        return order_ids





class pos_order_line(models.Model):
    _inherit = "pos.order.line"

    combo_items = fields.Text('Combo items', readonly=1)