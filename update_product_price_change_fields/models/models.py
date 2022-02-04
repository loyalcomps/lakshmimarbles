# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class product_barcode(models.Model):
    _inherit = 'product.barcode'

    @api.depends('landing_cost', 'product_mrp')
    def get_margin_value(self):
        for line in self:
            if line.product_mrp:
                line.margin = line.product_mrp - line.landing_cost
                line.margin_per = (line.margin / line.product_mrp) * 100

    margin = fields.Float('Margin', digits=dp.get_precision('Product Price'), store=True, compute="get_margin_value", )
    margin_per = fields.Float('Margin %', digits=dp.get_precision('Product Price'), store=True, compute="get_margin_value", )

    margin_discount = fields.Float('Margin Discount', default=0)
    margin_discount_per = fields.Float('Margin Discount(%)', default=0)
    flag_margin = fields.Boolean(string='Margin Flag', default=True)
    landing_cost = fields.Float(string="Landing Cost", )

    @api.onchange('product_mrp')
    def get_margin_discount_per(self):
        for line in self:
            if line.flag_margin == False:
                line.flag_margin = True
                return
            if line.margin_discount and line.product_mrp:
                line.margin_discount_per = (line.margin_discount * 100) / (line.product_mrp - line.landing_cost)
                line.flag_margin = False

    @api.onchange('margin_discount')
    def calculate_margin_discount_per(self):
        for line in self:
            if line.flag_margin == False:
                line.flag_margin = True
                return
            if line.margin:
                line.margin_discount_per = (line.margin_discount * 100) / line.margin
                line.flag_margin = False
            else:
                line.margin_discount_per = 0
                line.flag_margin = False

    @api.onchange('margin_discount_per')
    def calculate_margin_discount(self):
        for line in self:
            if line.flag_margin == False:
                line.flag_margin = True
                return
            if line.margin:
                line.margin_discount = (line.margin * line.margin_discount_per) / 100
                line.flag_margin = False
            else:
                line.margin_discount = 0
                line.flag_margin = False

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):

        res=super(StockPicking, self).do_transfer()
        for record in self:
            for line in record.pack_operation_product_ids:
                if line.landing_cost:
                    if line.multi_barcode:

                        line.multi_barcode.write({'landing_cost': line.landing_cost})
                    else:
                        products=line.product_id
                        products.write({'landing_cost':line.landing_cost})
        return res

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()

        for record in self:
            if record.type == 'in_invoice':

                for line in record.invoice_line_ids:
                    if line.multi_barcodes:
                        line.multi_barcodes.write({
                            'margin': line.margin,
                            'margin_per': line.margin_per,
                            'margin_discount': line.margin_discount,
                            'margin_discount_per': line.margin_discount_per,
                        })
                    else:
                        products = line.product_id
                        products.write({
                            'margin': line.margin,
                            'margin_per': line.margin_per,
                            'margin_discount': line.margin_discount,
                            'margin_discount_per': line.margin_discount_per,
                        })
        return  res
