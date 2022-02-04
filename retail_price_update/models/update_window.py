# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class UpdateWindow(models.Model):
    _name = 'update.window'

    name = fields.Char(required=True, index=True, copy=False, default='New')
    user_id = fields.Many2one('res.users', string='User', readonly=True,
        states={'draft': [('readonly', False)]},default=lambda self: self.env.user)
    # date = fields.Date(string='Date',)
    confirm_id = fields.Many2one('confirm.window', string='Confirm Reference', domain=([('state','=','confirm'),('confirm_line_ids.confirm','=',False)]))
    planned_date = fields.Date(string='Planned Date', default=fields.Date.context_today, copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, )

    state = fields.Selection([
                ('draft', 'Draft'),
                ('updated', 'Updated'),
                ('cancel', 'Cancelled'),
            ], string='Status', index=True, readonly=True, default='draft',
            track_visibility='onchange', copy=False,
        )
    update_line_ids = fields.One2many('update.window.line', 'update_id', string='Product Info',
            readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    company_id = fields.Many2one('res.company', string='Company', store=True,
                                 readonly=True,default=lambda self: self.env.user.company_id.id)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('update.window') or '/'
        return super(UpdateWindow, self).create(vals)

    @api.onchange('confirm_id')
    def load_product_based_confirm_id(self):
        if not self.confirm_id:
            return {}
        confirm_line_id = self.env['confirm.window.line'].search(
            [('confirm_id.id', '=', self.confirm_id.id), ('confirm_id.state', '=', 'confirm'),
             ('confirm', '=', False)])
        if not confirm_line_id:
            self.confirm_id = False
            return {

                'warning': {'title': 'Error!', 'message': 'Please Choose Another Reference'},
                'value': {
                    'confirm_id': False,

                }
            }
        for rec in confirm_line_id:
            if rec in self.update_line_ids.mapped('confirm_line_id'):
                return
            order_line_var = self.env['update.window.line']
            values = {
                'product_id': rec.product_id.id,
                'current_price': rec.product_id.lst_price,
                'new_price': rec.new_price,
                'mrp': rec.mrp,
                'on_hand': rec.product_id.qty_available,
                'date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'confirm_line_id': rec.id

            }
            order_line_var1 = order_line_var.new(values)
            order_line_var += order_line_var1
            self.update_line_ids += order_line_var
        self.confirm_id = False

    # @api.onchange('date')
    # def load_product_based_date(self):
    #     if not self.date:
    #         return {}
    #     confirm_id = self.env['confirm.window.line'].search([('confirm_id.date','=',self.date),('confirm_id.state','=','confirm'),
    #                                                          ('confirm','=',False)])
    #     if not confirm_id:
    #         self.date = False
    #         return {
    #
    #             'warning': {'title': 'Error!', 'message': 'Please Choose Another Date'},
    #             'value': {
    #                 'date': False,
    #
    #             }
    #         }
    #     for rec in confirm_id:
    #         order_line_var = self.env['update.window.line']
    #         values = {
    #             'product_id': rec.product_id.id,
    #             'current_price': rec.product_id.lst_price,
    #             'new_price': rec.new_price,
    #             'mrp': rec.mrp,
    #             'on_hand': rec.product_id.qty_available,
    #             'date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    #             'confirm_line_id':rec.id
    #
    #         }
    #         order_line_var1 = order_line_var.new(values)
    #         order_line_var += order_line_var1
    #         self.update_line_ids += order_line_var
    #     self.date = False

    @api.multi
    def button_update(self):
        for rec in self:
            rec.write({'state': 'updated'})
            for line in rec.update_line_ids:
                line.confirm_line_id.confirm = True
                line.product_id.lst_price=line.new_price

    @api.multi
    def button_cancel(self):
        for rec in self:
            rec.write({'updated': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ['updated', 'cancel']:
                raise UserError(_('Cannot delete a record which is in state \'%s\'.') % (rec.state,))

        return super(UpdateWindow, self).unlink()



class UpdateWindowLine(models.Model):
    _name = 'update.window.line'


    update_id = fields.Many2one('update.window', string='Update Reference',
                                 ondelete='cascade', index=True)
    confirm_line_id = fields.Many2one('confirm.window.line', string='Confirm Reference',)
    product_id = fields.Many2one('product.product', string='Product',
                                 ondelete='restrict', index=True,)
    new_price = fields.Float(string='New Price', required=True, digits=dp.get_precision('Product Price'),default=0,readonly=True)
    current_price = fields.Float(string='Current Price', readonly=True, digits=dp.get_precision('Product Price'),default=0)
    mrp = fields.Float(string="MRP",default=0,readonly=True,)
    on_hand=fields.Float(string="Onhand",default=0,readonly=True,)
    user_id = fields.Many2one('res.users', string='User',related="update_id.user_id")
    date = fields.Date(string='Date', default=fields.Date.context_today, copy=False, readonly=True )
    company_id = fields.Many2one('res.company', related='update_id.company_id', string='Company', store=True,
                                 readonly=True)

    @api.multi
    def unlink(self):
        for line in self:
            if line.update_id.state in ['updated', 'cancel']:
                raise UserError(_('Cannot delete a product line which is in state \'%s\'.') % (line.update_id.state,))

        return super(UpdateWindowLine, self).unlink()


    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     result = {}
    #     if not self.product_id:
    #         return result
    #     self.date = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    #     self.current_price = self.product_id.lst_price
    #     self.cost = self.product_id.taxed_cost
    #     self.mrp = self.product_id.product_mrp
    #     self.on_hand = self.product_id.qty_available

