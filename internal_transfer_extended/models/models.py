# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, AccessError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.depends('product_id')
    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.picking_id.move_lines:
                line_rec.sl_no = line_num
                line_num += 1

    barcode_scan = fields.Char(string='Product Barcode', help="Here you can provide the barcode for the product")
    multi_barcode = fields.Many2one('product.barcode', string="multi Barcode", )
    sl_no = fields.Integer(compute='_get_line_numbers', string='Sl No.', readonly=False, store=True)
    landing_cost = fields.Float(string="Landing Cost",default=0.0,store=True,)
    product_mrp = fields.Float(string="MRP",default=0.0,store=True,)
    sale_price = fields.Float(string="Sale Price", default=0.0,store=True,)

    #grn print-Arya
    free_qty = fields.Float(string='Free Qty', default=0)
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])

    discount_amount = fields.Float(string="Discount(amt)", default=0.0)
    discount_percentage = fields.Float(string="Discount(%)", default=0.0)
    # inclusive_value = fields.Boolean('inclusive', default=False)
    #grn - end

    @api.onchange('product_id','multi_barcode')
    def change_multi_barcode(self):


        if self.product_id and not self.multi_barcode:
            res = {'landing_cost':self.product_id.landing_cost,
                   'product_mrp':self.product_id.product_mrp,
                   'sale_price':self.product_id.lst_price}
            self.update(res)

        if self.product_id and self.multi_barcode:
            res = {'landing_cost': self.product_id.landing_cost,
                   'product_mrp': self.multi_barcode.product_mrp,
                   'sale_price': self.multi_barcode.list_price}
            self.update(res)


    @api.onchange('barcode_scan', 'product_id')
    def _onchange_barcode_scan(self):
        product_rec = self.env['product.product']
        product_ids = []
        result = {}
        if self.barcode_scan:
            product = product_rec.search([('barcode', '=', self.barcode_scan)])
            if product:
                product_ids.append(product.id)

            product_tmpl_ids = self.env['product.barcode'].search([('barcode', '=', self.barcode_scan)])

            for product_tmpl in product_tmpl_ids:
                product = product_rec.search([('product_tmpl_id', '=', product_tmpl.product_tmpl_id.id)])
                product_ids.append(product.id)
            # if len(product_ids) == 1:
            #     self.product_id = product_ids[0]
            # else:
            result['domain'] = {'product_id': [('id', 'in', product_ids)]}

            return result
        else:
            products = self.env['product.product'].search([]).ids
            result['domain'] = {'product_id': [('id', 'in', products)]}

            return result

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def _prepare_stock_moves(self, picking):
        res=super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        if len(res)>0:

            res[0].update({
                'product_mrp':self.product_mrp,
                'sale_price':self.sale_price,
                'landing_cost':self.landing_cost,
                'free_qty':self.free_qty,
                'taxes_id':[(6, 0, self.taxes_id.ids)],
                'multi_barcode':self.multi_barcode.id,
                'discount_amount': self.discount_amount,
                'discount_percentage': self.discount_percentage,

            })
        return res
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # @api.model
    # def _prepare_picking(self):
    #     if not self.group_id:
    #         self.group_id = self.group_id.create({
    #             'name': self.name,
    #             'partner_id': self.partner_id.id
    #         })
    #     if not self.partner_id.property_stock_supplier.id:
    #         raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
    #     return {
    #         'picking_type_id': self.picking_type_id.id,
    #         'partner_id': self.partner_id.id,
    #         'date': self.date_order,
    #         'origin': self.name,
    #         'location_dest_id': self._get_destination_location(),
    #         'location_id': self.partner_id.property_stock_supplier.id,
    #         'company_id': self.company_id.id,
    #         'inclusive_value': self.inclusive_value
    #     }

    @api.model
    def _prepare_picking(self):
        picking_vals = super(PurchaseOrder, self)._prepare_picking()
        picking_vals['inclusive_value'] = self.inclusive_value if self.inclusive_value else False
        return picking_vals

