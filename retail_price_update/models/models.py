# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    old_cost = fields.Float(string="Old Cost",store=True,default=0)

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        self.old_cost = self.product_id.landing_cost

    @api.onchange('multi_barcode')
    def load_multibarcode_product(self):
        super(PurchaseOrderLine, self).load_multibarcode_product()
        if self.multi_barcode:
            self.old_cost = self.multi_barcode.landing_cost
        else:
            self.old_cost = self.product_id.landing_cost


class ProductProduct(models.Model):
    _inherit = 'product.product'

    new_price = fields.Float('New Retail Price',digits=dp.get_precision('Product Price'), default=0)

    profit = fields.Float(string='Profit', default=0)

    profit_perc = fields.Float(string='Profit%', default=0)

    # taxed_cost = fields.Float(
    #     'Taxed Cost', digits=dp.get_precision('Product Price'),default=0)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    new_price = fields.Float('New Retail Price', digits=dp.get_precision('Product Price'), related='product_variant_ids.new_price',
                          store=True)

    profit = fields.Float(string='Profit', default=0,related='product_variant_ids.profit',)

    profit_perc = fields.Float(string='Profit%', default=0,related='product_variant_ids.profit_perc',)


class product_barcode(models.Model):
    _inherit = 'product.barcode'

    new_price = fields.Float('New Retail Price', digits=dp.get_precision('Product Price'), store=True,)

    profit = fields.Float(string='Profit', default=0)

    profit_perc = fields.Float(string='Profit%', default=0)

#     taxed_cost = fields.Float(
#         'Taxed Cost',
#         digits=dp.get_precision('Product Price'),default=0 )
#
# class PackOperation(models.Model):
#     _inherit = 'stock.pack.operation'
#
#     @api.depends('qty_done', 'price_unit', 'taxes_id')
#     def _compute_amount(self):
#         res=super(PackOperation, self)._compute_amount()
#         s=0
#
#
#         for line in self:
#             qty = 0
#             if line.free_qty and line.qty_done:
#                 qty = line.qty_done - line.free_qty
#             else:
#                 qty = line.qty_done
#             if line.picking_id.purchase_id and qty!=0:
#                 line.product_id.write({'taxed_cost':line.price_total/qty})
#
#
