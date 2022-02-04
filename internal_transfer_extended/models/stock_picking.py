# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from collections import namedtuple
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import odoo.addons.decimal_precision as dp

class Picking(models.Model):
    _inherit = 'stock.picking'

    # grn print - Arya



    @api.depends('pack_operation_product_ids.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = amount_discount = net_amount = 0.0
            for line in order.pack_operation_product_ids:
                if order.inclusive_value:
                    net_taxes = line.taxes_id.with_context(price_include=True,
                                                       include_base_amount=True).compute_all_inc(line.price_unit,
                                                                                                 line.picking_id.currency_id,
                                                                                                 line.product_qty - line.free_qty,
                                                                                                 product=line.product_id,
                                                                                                 partner=None)
                else:

                    net_taxes = line.taxes_id.compute_all(line.price_unit, line.picking_id.currency_id, line.product_qty - line.free_qty,
                                                      product=line.product_id, partner=None)
                net_amount +=net_taxes['total_included']
                amount_untaxed += line.price_subtotal
                amount_discount += line.discount_amount
                # FORWARDPORT UP TO 10.0
                price = line.price_unit * (1 - ((line.discount_percentage or 0.0) / 100.0))
                if order.company_id.tax_calculation_rounding_method == 'round_globally':


                    if order.inclusive_value:

                        taxes = line.taxes_id.with_context(price_include=True,
                                                           include_base_amount=True).compute_all_inc(price,
                                                                                                     line.picking_id.currency_id,
                                                                                                     line.product_qty - line.free_qty,
                                                                                                     product=line.product_id,
                                                                                                     partner=None)
                    else:

                        taxes = line.taxes_id.compute_all(price, line.picking_id.currency_id, line.product_qty-line.free_qty,
                                                      product=line.product_id, partner=None)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))



                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
                'amount_discount': order.currency_id.round(amount_discount),
                'net_amount': order.currency_id.round(net_amount)
            })

    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')

    amount_discount = fields.Monetary(string="Discount", store=True, readonly=True, track_visibility='always',
                                      compute="_amount_all")
    net_amount = fields.Monetary(string="Net Amount", store=True, readonly=True, track_visibility='always',
                                 compute="_amount_all")

    inclusive_value = fields.Boolean('inclusive', default=False)




    # grn print - Arya end

    def _prepare_pack_ops(self, quants, forced_qties):
        """ Prepare pack_operations, returns a list of dict to give at create """
        # TDE CLEANME: oh dear ...



        valid_quants = quants.filtered(lambda quant: quant.qty > 0)
        _Mapping = namedtuple('Mapping', ('product', 'package', 'owner', 'location', 'location_dst_id','barcode','landing_cost','product_mrp',
                                          'sale_price','free_qty','taxes_id','price_unit','discount_amount','discount_percentage','multi_barcode'))

        all_products = valid_quants.mapped('product_id') | self.env['product.product'].browse(p.id for p in forced_qties.keys()) | self.move_lines.mapped('product_id')
        computed_putaway_locations = dict(
            (product, self.location_dest_id.get_putaway_strategy(product) or self.location_dest_id.id) for product in all_products)

        product_to_uom = dict((product.id, product.uom_id) for product in all_products)
        picking_moves = self.move_lines.filtered(lambda move: move.state not in ('done', 'cancel'))
        for move in picking_moves:
            # If we encounter an UoM that is smaller than the default UoM or the one already chosen, use the new one instead.
            if move.product_uom != product_to_uom[move.product_id.id] and move.product_uom.factor > product_to_uom[move.product_id.id].factor:
                product_to_uom[move.product_id.id] = move.product_uom
        if len(picking_moves.mapped('location_id')) > 1:
            raise UserError(_('The source location must be the same for all the moves of the picking.'))
        if len(picking_moves.mapped('location_dest_id')) > 1:
            raise UserError(_('The destination location must be the same for all the moves of the picking.'))

        pack_operation_values = []
        # find the packages we can move as a whole, create pack operations and mark related quants as done
        top_lvl_packages = valid_quants._get_top_level_packages(computed_putaway_locations)
        for pack in top_lvl_packages:
            pack_quants = pack.get_content()
            pack_operation_values.append({
                'picking_id': self.id,
                'package_id': pack.id,
                'product_qty': 1.0,
                'location_id': pack.location_id.id,
                'location_dest_id': computed_putaway_locations[pack_quants[0].product_id],
                'owner_id': pack.owner_id.id,
            })
            valid_quants -= pack_quants

        # Go through all remaining reserved quants and group by product, package, owner, source location and dest location
        # Lots will go into pack operation lot object

        qtys_grouped = {}
        lots_grouped = {}
        barcode = ''
        landing_cost = 0
        product_mrp = 0
        sale_price = 0
        free_qty = 0
        price_unit =0
        discount_amount = 0
        discount_percentage = 0
        multi_barcode = False


        taxes_id =self.env['account.tax']
        for quant in valid_quants:
            for move in picking_moves:
                if move.reserved_quant_ids==quant.id:
                    barcode=move.multi_barcod.barcode if move.multi_barcode else move.product_id.barcode
                    landing_cost = move.landing_cost if move.landing_cost else 0
                    product_mrp = move.product_mrp if move.product_mrp else 0
                    sale_price = move.sale_price if move.sale_price else 0
                    free_qty = move.free_qty if move.free_qty else 0
                    discount_amount = move.discount_amount if move.discount_amount else 0
                    discount_percentage = move. discount_percentage if move. discount_percentage else 0
                    taxes_id = [(6, 0, move.taxes_id.ids)]
                    multi_barcode = move.multi_barcode.id
                    price_unit = move.price_unit if move.price_unit else 0


            key = _Mapping(quant.product_id, quant.package_id, quant.owner_id, quant.location_id, computed_putaway_locations[quant.product_id],
                           barcode,landing_cost,product_mrp,sale_price,free_qty,taxes_id,price_unit,discount_amount,discount_percentage,multi_barcode)
            qtys_grouped.setdefault(key, 0.0)
            qtys_grouped[key] += quant.qty
            if quant.product_id.tracking != 'none' and quant.lot_id:
                lots_grouped.setdefault(key, dict()).setdefault(quant.lot_id.id, 0.0)
                lots_grouped[key][quant.lot_id.id] += quant.qty
        # Do the same for the forced quantities (in cases of force_assign or incomming shipment for example)
        for product, value in forced_qties.items():
            for key,item in value.items():
                if key =='barcode':
                    barcode= product.barcode
                    multi_barcode = False
                else:
                    barcode = self.env['product.barcode'].browse(key.id).barcode
                    multi_barcode = key.id

                if item[0] <= 0.0:
                    continue
                key = _Mapping(product, self.env['stock.quant.package'], self.owner_id, self.location_id, computed_putaway_locations[product],barcode,
                               item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8],multi_barcode)
                qtys_grouped.setdefault(key, 0.0)
                qtys_grouped[key] += item[0]

        # Create the necessary operations for the grouped quants and remaining qtys
        Uom = self.env['product.uom']
        product_id_to_vals = {}  # use it to create operations using the same order as the picking stock moves
        for mapping, qty in qtys_grouped.items():
            uom = product_to_uom[mapping.product.id]
            val_dict = {
                'picking_id': self.id,
                'product_qty': mapping.product.uom_id._compute_quantity(qty, uom),
                'product_id': mapping.product.id,
                'package_id': mapping.package.id,
                'owner_id': mapping.owner.id,
                'location_id': mapping.location.id,
                'location_dest_id': mapping.location_dst_id,
                'barcode': mapping.barcode,
                'multi_barcode':mapping.multi_barcode,
                'landing_cost': mapping.landing_cost,
                'product_mrp': mapping.product_mrp,
                'sale_price': mapping.sale_price,
                'free_qty':mapping.free_qty,
                'discount_amount':mapping.discount_amount,
                'discount_percentage' :mapping.discount_percentage,
                'taxes_id':[(6, 0, mapping.taxes_id.ids)],
                'price_unit':mapping.price_unit,
                'product_uom_id': uom.id,
                'pack_lot_ids': [
                    (0, 0, {
                        'lot_id': lot,
                        'qty': 0.0,
                        'qty_todo': mapping.product.uom_id._compute_quantity(lots_grouped[mapping][lot], uom)
                    }) for lot in lots_grouped.get(mapping, {}).keys()],
            }
            product_id_to_vals.setdefault(mapping.product.id, list()).append(val_dict)

        for move in self.move_lines.filtered(lambda move: move.state not in ('done', 'cancel')):
            values = product_id_to_vals.pop(move.product_id.id, [])
            pack_operation_values += values
        return pack_operation_values

    @api.multi
    def do_prepare_partial(self):
        # TDE CLEANME: oh dear ...
        PackOperation = self.env['stock.pack.operation']

        # get list of existing operations and delete them
        existing_packages = PackOperation.search([('picking_id', 'in', self.ids)])  # TDE FIXME: o2m / m2o ?
        if existing_packages:
            existing_packages.unlink()
        for picking in self:
            forced_qties = {}  # Quantity remaining after calculating reserved quants
            picking_quants = self.env['stock.quant']
            # Calculate packages, reserved quants, qtys of this picking's moves
            for move in picking.move_lines:
                if move.state not in ('assigned', 'confirmed', 'waiting'):
                    continue
                move_quants = move.reserved_quant_ids
                picking_quants += move_quants
                forced_qty = 0.0
                # discount_amount=0.0
                # discount_percentage = 0.0
                if move.state == 'assigned':
                    qty = move.product_uom._compute_quantity(move.product_uom_qty, move.product_id.uom_id, round=False)
                    forced_qty = qty - sum([x.qty for x in move_quants])
                # if we used force_assign() on the move, or if the move is incoming, forced_qty > 0
                if float_compare(forced_qty, 0, precision_rounding=move.product_id.uom_id.rounding) > 0:
                    if move.multi_barcode:

                        if forced_qties.get(move.product_id):
                            if move.multi_barcode in forced_qties[move.product_id]:
                                forced_qties[move.product_id][move.multi_barcode][0] += forced_qty
                                forced_qties[move.product_id][move.multi_barcode][4] += move.free_qty
                            else:
                                forced_qties[move.product_id][move.multi_barcode]= [forced_qty,move.landing_cost,move.product_mrp,move.sale_price,move.free_qty,move.taxes_id,move.price_unit,move.discount_amount,move.discount_percentage]
                        else:
                            forced_qties[move.product_id] = {move.multi_barcode:[forced_qty,move.landing_cost,move.product_mrp,move.sale_price,move.free_qty,move.taxes_id,move.price_unit,move.discount_amount,move.discount_percentage]}
                    else:
                        if forced_qties.get(move.product_id):
                            if 'barcode' in forced_qties[move.product_id]:
                                forced_qties[move.product_id]['barcode'][0] += forced_qty
                                forced_qties[move.product_id]['barcode'][4] += move.free_qty
                            else:
                                forced_qties[move.product_id]['barcode']= [forced_qty,move.landing_cost,move.product_mrp,move.sale_price,move.free_qty,move.taxes_id,move.price_unit,move.discount_amount,move.discount_percentage]
                        else:
                            forced_qties[move.product_id] = {'barcode':[forced_qty,move.landing_cost,move.product_mrp,move.sale_price,move.free_qty,move.taxes_id,move.price_unit,move.discount_amount,move.discount_percentage]}

            for vals in picking._prepare_pack_ops(picking_quants, forced_qties):
                vals['fresh_record'] = False
                PackOperation |= PackOperation.create(vals)
        # recompute the remaining quantities all at once
        self.do_recompute_remaining_quantities()
        for pack in PackOperation:
            pack.ordered_qty = sum(
                pack.mapped('linked_move_operation_ids').mapped('move_id').filtered(
                    lambda r: r.state != 'cancel').mapped('ordered_qty')
            )
        self.write({'recompute_pack_op': False})

class PackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    # sl_no = fields.Integer(compute='_get_line_numbers', string='Sl No.', readonly=False, store=True)
    barcode = fields.Char(string='Barcode', help="Here you can provide the barcode for the product")
    multi_barcode = fields.Many2one('product.barcode', string="multi Barcode", )
    landing_cost = fields.Float(string="Landing Cost",)
    product_mrp = fields.Float(string="MRP")
    sale_price = fields.Float(string="Sale Price", default=0.0)

    discount_amount = fields.Float(string="Discount(amt)", default=0.0)
    discount_percentage = fields.Float(string="Discount(%)", default=0.0)

    #grn Print -Arya
    @api.depends('qty_done', 'price_unit', 'taxes_id')
    def _compute_amount(self):


        for line in self:
            qty = 0
            if line.free_qty and line.qty_done:
                qty=line.qty_done-line.free_qty
            else:
                qty = line.qty_done
            price = line.price_unit * (1 - ((line.discount_percentage or 0.0) / 100.0))
            if line.picking_id.inclusive_value:
                taxes = self.taxes_id.with_context(price_include=True,
                                                               include_base_amount=True).compute_all_inc(price,
                                                                                                         line.picking_id.currency_id, qty,
                                                                                            product=line.product_id, partner=None)
            else:

                taxes = line.taxes_id.compute_all(price, line.picking_id.currency_id, qty,
                                              product=line.product_id, partner=None)
            # taxes = line.taxes_id.compute_all(line.price_unit, line.picking_id.currency_id, qty,
            #                                   product=line.product_id, partner=None)
            foc_amount = 0
            if line.free_qty:
                free_qty_taxes = line.taxes_id.compute_all(line.price_unit, line.picking_id.currency_id, line.free_qty,
                                                           product=line.product_id, partner=None)
                foc_amount = free_qty_taxes['total_excluded']
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'foc_amount': foc_amount
            })

    free_qty = fields.Float(string='Free Qty', default=0)
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Tax', store=True)
    foc_amount = fields.Monetary(compute='_compute_amount', string='FOC Taxable', store=True)
    #grn print -end

