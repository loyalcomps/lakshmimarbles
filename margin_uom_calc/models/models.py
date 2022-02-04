# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"


    @api.depends('product_uom.factor_inv','product_uom.factor')
    @api.onchange('product_uom')
    def get_ratio_value(self):
        for line in self:
            if line.product_uom.factor_inv:
                line.ratio=line.product_uom.factor_inv
            elif line.product_uom.factor:
                line.ratio = line.product_uom.factor



    ratio = fields.Float(string="Ratio", compute="get_ratio_value", store=True)
    cart_rate =fields.Float(string="Cart Rate",store=True)

    @api.onchange('cart_rate')
    @api.depends('cart_rate','product_uom','ratio')
    def get_price_unit_value(self):
        for line in self:
            if line.ratio!=0:
                line.price_unit=line.cart_rate/line.ratio


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):

        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        for l in line:
            var = {

                'ratio':l.ratio,
                'cart_rate':l.cart_rate

            }
        res.update(var)
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.depends('uom_id')
    def get_ratio_value(self):
        for line in self:
            if line.uom_id.factor_inv:
                line.ratio = line.uom_id.factor_inv
            elif line.uom_id.factor:
                line.ratio = line.uom_id.factor



    ratio = fields.Float(string="Ratio",compute="get_ratio_value",  store=True)
    cart_rate =fields.Float(string="Cart Rate",store=True)

    @api.onchange('cart_rate')
    @api.depends('cart_rate','uom_id','ratio')
    def get_account_priceunit_value(self):
        for line in self:
            if line.ratio!=0:
                line.price_unit=line.cart_rate/line.ratio
