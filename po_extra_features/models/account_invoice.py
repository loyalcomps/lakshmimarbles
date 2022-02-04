# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):

        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        for l in line:
            var = {

                'margin_discount':l.margin_discount,
                'margin_discount_per':l.margin_discount_per,

            }
        res.update(var)
        return res

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.depends('product_mrp')
    def get_landing_cost(self):
        res=super(AccountInvoiceLine, self).get_landing_cost()
        for line in self:
            if line.product_mrp:
                line.margin = line.product_mrp - line.landing_cost
                line.margin_per = (line.margin / line.product_mrp) * 100


    margin = fields.Float('Margin', digits=dp.get_precision('Product Price'), default=0,compute="get_landing_cost",
                store = True )
    margin_per = fields.Float('Margin %', digits=dp.get_precision('Product Price'), default=0, compute="get_landing_cost",
                          store=True)
    margin_discount = fields.Float(string='Margin Discount', digits=dp.get_precision('Product Price'), default=0,store=True)
    margin_discount_per = fields.Float(string='Margin Discount(%)', digits=dp.get_precision('Product Price'),
                                       default=0,store=True)
    flag_margin=fields.Boolean(string='Margin Flag',default=True)

    @api.onchange('product_mrp')
    def get_margin_discount_per(self):
        for line in self:
            if line.flag_margin==False:
                line.flag_margin = True
                return
            if line.product_mrp and line.margin_discount:
                line.margin_discount_per = (line.margin_discount * 100) / (line.product_mrp-line.landing_cost) if (line.product_mrp-line.landing_cost) !=0 else 0
                line.flag_margin = False


    @api.onchange('margin_discount')
    def calculate_margin_discount_per(self):
        for line in self:
            if line.flag_margin==False:
                line.flag_margin = True
                return
            if line.margin:
                line.margin_discount_per = (line.margin_discount*100)/line.margin
                line.flag_margin = False


    @api.onchange('margin_discount_per')
    def calculate_margin_discount(self):
        for line in self:
            if line.flag_margin==False:
                line.flag_margin = True
                return
            if line.margin:
                line.margin_discount = (line.margin*line.margin_discount_per) / 100
                line.flag_margin = False


    @api.onchange('margin_discount_per','margin_discount','margin','product_mrp')
    def calculate_sale_price(self):
        for line in self:
            if line.product_mrp and line.margin_discount:
                line.sale_price = line.product_mrp - line.margin_discount

