# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError



class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_expense_line_ids = fields.One2many('purchase.expense', 'purchase_id', string='Purchase Expense',
                                                readonly=True, states={'draft': [('readonly', False)]} )
    expense = fields.Monetary(string="Purchase Expense", store=True, readonly=True, track_visibility='always',
                                     compute="_amount_all")

    @api.depends('purchase_expense_line_ids')
    def compute_total_expense(self):
        for order in self:
            expense = 0
            for line in order.purchase_expense_line_ids:
                expense += line.rate
                order.update({
                    'total_expense': expense
                })

    total_expense = fields.Float(string="Total Expense", store=True,compute="compute_total_expense")



    @api.one
    @api.depends('purchase_expense_line_ids')
    def _amount_all(self):
        res = super(PurchaseOrder, self)._amount_all()

        for order in self:
            expense = 0

            for line in order.purchase_expense_line_ids:
                expense += line.rate if line.exp_to_total==True else 0
            order.update({
                'amount_total':order.amount_total+expense,
                'expense':expense
            })

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('order_id.purchase_expense_line_ids')
    def get_landing_cost(self):
        res=super(PurchaseOrderLine, self).get_landing_cost()
        expense = 0
        # for line in self:
        #     for line in line.order_id.purchase_expense_line_ids:
        #         expense += line.rate
        for line in self:
            expense=line.order_id.total_expense
            total_amount = line.order_id.amount_untaxed + line.order_id.amount_tax
            line_expense = (expense*line.price_total)/(total_amount*line.product_qty) if (total_amount*line.product_qty)!=0 else 0
            line_expense_unit = line.product_uom._compute_price(line_expense, line.product_id.uom_po_id) \
                if line.product_id.uom_po_id != line.product_uom else line_expense
            line.landing_cost = line.landing_cost +line_expense_unit
            line.margin = line.product_mrp - line.landing_cost
            line.margin_per = (line.margin / line.product_mrp) * 100 if line.product_mrp else 0




class PurchaseExpense(models.Model):
    _name = 'purchase.expense'


    purchase_id = fields.Many2one('purchase.order', string='Purchase', ondelete='cascade',)
    name = fields.Selection([
            ('freight', 'Freight Charge'),
            ('union', 'Union Charge'),
            ('packing', 'Packing Charge'),
        ('other','Other Charges'),
        ], string='Expense', required=True,)
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env['res.company']._company_default_get('purchase.expense'))

    rate = fields.Float(string = 'Amount',digits=dp.get_precision('Discount'),default=0.0)
    exp_to_total = fields.Boolean(string='Expense to Toal', default=True)

