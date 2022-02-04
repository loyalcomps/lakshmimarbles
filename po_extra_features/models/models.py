# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    discount = fields.Float(string="Discount", digits=dp.get_precision('Discount'), default=0.0)
    discount_type = fields.Selection([('percent', "Percentage"), ('amount', "Amount")], string="Discount type")
    discount_amt = fields.Float(string="Discount", digits=dp.get_precision('Discount'), default=0.0, store=True)
    round_off_value = fields.Float(string="Round Off", default=0.0)
    round_off_operation = fields.Selection([('plus', '+'), ('minus', '-')], string='Round Off Operation')
    rounded_total = fields.Float(compute='_amount_all', string='Rounded Value', default=0.0)

    @api.onchange('discount_type', 'discount', )
    def _onchange_discount(self):
        disc_amount = 0
        if self.discount_type == "amount":
            if self.discount >= self.amount_untaxed + self.amount_tax:
                raise UserError(('Cannot give discount more than total amount.'))
            self.discount_amt = self.discount
        if self.discount_type == "percent":
            disc_amount = ((self.amount_untaxed + self.amount_tax) * self.discount) / 100
            if disc_amount >= self.amount_untaxed + self.amount_tax:
                raise UserError(('Cannot give discount more than total amount.'))
            self.discount_amt = disc_amount

    @api.one
    @api.depends('order_line.price_subtotal', 'discount_amt','round_off_value','round_off_operation')
    def _amount_all(self):

        res = super(PurchaseOrder, self)._amount_all()
        for order in self:
            if order.round_off_operation == 'plus' and order.amount_total:
                rounded_total = order.round_off_value
            elif order.round_off_operation == 'minus' and order.amount_total:
                rounded_total = order.round_off_value * -1
            else:
                rounded_total =0

            order.update({
                'rounded_total':rounded_total,
                'amount_discount':order.amount_discount+order.discount_amt,
                'amount_total': order.amount_total -order.discount_amt+rounded_total,
            })

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.discount_type and self.purchase_id.discount_type:
            self.discount_type = self.purchase_id.discount_type
        if not self.discount and self.purchase_id.discount:
            self.discount = self.purchase_id.discount
        if not self.round_off_value and self.purchase_id.round_off_value:
            self.round_off_value = self.purchase_id.round_off_value
        if not self.round_off_operation and self.purchase_id.round_off_operation:
            self.round_off_operation = self.purchase_id.round_off_operation
        return super(AccountInvoice, self).purchase_order_change()

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('product_qty', 'price_total', 'order_id.amount_untaxed', 'order_id.amount_tax', 'order_id.discount_amt', 'product_mrp')
    def get_landing_cost(self):
        for line in self:
            unit_amount= line.price_total/line.product_qty if line.product_qty != 0 else 0
            total_amount=line.order_id.amount_untaxed+line.order_id.amount_tax
            line_discount= (line.order_id.discount_amt*line.price_total)/total_amount if total_amount != 0 else 0
            unit_discount = line_discount/line.product_qty if line.product_qty != 0 else 0
            line.landing_cost = line.product_uom._compute_price((unit_amount-unit_discount), line.product_id.uom_po_id) \
                if line.product_id.uom_po_id != line.product_uom else (unit_amount-unit_discount)
            line.margin = line.product_mrp - line.landing_cost
            line.margin_per = (line.margin/line.product_mrp)*100 if line.product_mrp else 0

    landing_cost = fields.Float(string="Landing Cost", compute="get_landing_cost", store=True)
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
            # if line.product_mrp and not line.margin_discount and line.margin_discount_per:
            #     line.sale_price = line.product_mrp - line.margin_discount

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    margin = fields.Float('Margin',digits=dp.get_precision('Product Price'),related='product_variant_ids.margin',store=True)
    margin_per = fields.Float('Margin %', digits=dp.get_precision('Product Price'), related='product_variant_ids.margin_per',
                          store=True)
    margin_discount = fields.Float('Margin Discount',default=0,related='product_variant_ids.margin_discount')
    margin_discount_per = fields.Float('Margin Discount(%)',default=0,related='product_variant_ids.margin_discount_per',store=True)
    flag_margin = fields.Boolean(string='Margin Flag', default=True,related='product_variant_ids.flag_margin')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('landing_cost', 'product_mrp')
    def get_margin_value(self):
        for line in self:
            if line.product_mrp:
                line.margin = line.product_mrp - line.landing_cost
                line.margin_per = (line.margin / line.product_mrp) * 100

    margin = fields.Float('Margin', digits=dp.get_precision('Product Price'),store=True,compute="get_margin_value",)
    margin_per = fields.Float('Margin %', digits=dp.get_precision('Product Price'), store=True, compute="get_margin_value", )

    margin_discount = fields.Float('Margin Discount', default=0)
    margin_discount_per = fields.Float('Margin Discount(%)', default=0)
    flag_margin = fields.Boolean(string='Margin Flag', default=True)

    @api.onchange('product_mrp')
    def get_margin_discount_per(self):
        for line in self:
            if line.flag_margin == False:
                line.flag_margin = True
                return
            if line.product_mrp:
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


    @api.onchange('margin_discount_per')
    def calculate_margin_discount(self):
        for line in self:
            if line.flag_margin == False:
                line.flag_margin = True
                return
            if line.margin:
                line.margin_discount = (line.margin * line.margin_discount_per) / 100
                line.flag_margin = False


    # @api.onchange('margin_discount_per', 'margin_discount', 'margin', 'product_mrp')
    # def calculate_sale_price(self):
    #     for line in self:
    #         if line.product_mrp and line.margin_discount:
    #             line.lst_price = line.product_mrp - line.margin_discount
