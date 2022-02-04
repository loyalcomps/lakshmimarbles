# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _prepare_picking(self):
        picking_vals = super(PurchaseOrder, self)._prepare_picking()
        new_lines = self.env['stock.expense']
        exp=[]

        for line in self.purchase_expense_line_ids:
            data = {
                'name': line.name,
                'company_id': line.company_id.id,
                'rate': line.rate,
                'exp_to_total':line.exp_to_total,
            }
            exp.append((0,0,data))
            # new_line = new_lines.new(data)
            # new_lines += new_line
        picking_vals.update({'purchase_expense_line_ids':exp,
                             })

        return picking_vals

class StockPicking(models.Model):
    _inherit = "stock.picking"

    purchase_expense_line_ids = fields.One2many('stock.expense', 'picking_id', string='Purchase Expense',
                                                readonly=True, states={'draft': [('readonly', False)]})
    expense = fields.Monetary(string="Purchase Expense", store=True, readonly=True, track_visibility='always',
                              compute="_amount_all")




    @api.depends('purchase_expense_line_ids')
    def _amount_all(self):

        res = super(StockPicking, self)._amount_all()
        for order in self:
            expense = 0
            for line in order.purchase_expense_line_ids:
                expense += line.rate if line.exp_to_total == True else 0

            order.update({
                'amount_total': order.amount_total + expense,
                'expense': expense
            })

class StockExpense(models.Model):
    _name = 'stock.expense'


    picking_id = fields.Many2one('stock.picking', string='Purchase', ondelete='cascade',)
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

