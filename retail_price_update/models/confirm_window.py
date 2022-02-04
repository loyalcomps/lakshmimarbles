# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError,ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ConfirmWindow(models.Model):
    _name = 'confirm.window'

    type = fields.Selection([('landed_cost','Landing Cost'),('category', 'Category'), ('product', 'Product'),('sale_price','Sale Price')
                             ,('po','Purchase Order')], string='Type', default="landed_cost",
                            required=True)
    purchase_id = fields.Many2one('purchase.order', string='Add Purchase Order',
                                  help='Encoding help. When selected, the associated purchase order lines are added to the Price Update. Several PO can be selected.',
                                  domain=[('state','in',['purchase','done'])])

    filter_date = fields.Date(string='Date Filter', copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, )
    category_id = fields.Many2one('product.category', string='Category')
    margin_discount = fields.Float(string='Margin Discount', digits=dp.get_precision('Product Price'), default=0,
                                   related='category_id.margin_discount')
    margin_discount_per = fields.Float(string='Margin Discount(%)', digits=dp.get_precision('Product Price'),
                                       default=0,related='category_id.margin_discount_per')

    name = fields.Char(required=True, index=True, copy=False, default='New')
    article = fields.Integer('Article No.', )
    barcode = fields.Char(string="Barcode")
    user_id = fields.Many2one('res.users', string='User', readonly=True,
        states={'draft': [('readonly', False)]},default=lambda self: self.env.user)
    date = fields.Date(string='Date',default=fields.Date.context_today, copy=False,readonly=True, states={'draft': [('readonly', False)]},)
    state = fields.Selection([
                ('draft', 'Draft'),
                ('confirm', 'Confirmed'),
                ('update','Updated'),
                ('cancel', 'Cancelled'),
            ], string='Status', index=True, readonly=True, default='draft',
            track_visibility='onchange', copy=False,
        )
    confirm_line_ids = fields.One2many('confirm.window.line', 'confirm_id', string='Product Info',
            readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    company_id = fields.Many2one('res.company', string='Company', store=True,
                                 readonly=True,default=lambda self: self.env.user.company_id.id)

    mrp_check = fields.Boolean(string='Margin Wise', default=True, required=True)
    profit = fields.Float(string='Profit', digits=dp.get_precision('Product Price'), default=0)
    profit_percentage = fields.Float('Profit (%)', default=0)

    def _prepare_confirm_line_from_po_line(self, line):

        data = {
            'purchase_line_id': line.id,
            'product_id': line.product_id.id,
            'article': line.product_id.id,
            'product_tmpl_id': line.product_id.product_tmpl_id.id,
            'landing_cost': line.landing_cost,
            'mrp': line.product_mrp,
            'current_price': line.product_id.lst_price,
            'new_price': line.sale_price,
            'mrp_check': True,
            'margin': line.margin,
            'margin_per': line.margin_per,
            'margin_discount': line.margin_discount,
            'margin_discount_per': line.margin_discount_per,
            'multi_barcode': line.multi_barcode,
        }

        return data

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}


        new_lines = self.env['confirm.window.line']
        value= self.env['confirm.window.line'].search([('confirm_id.type','=','po'),('confirm_id.state','!=','cancel'),
                            ('purchase_line_id','in',self.purchase_id.order_line.ids)])
        purchase=[]
        for record in value:
            purchase.append(record.purchase_line_id.id)
        purchase_lines= self.env['purchase.order.line'].search([('id','in',purchase)])
        for line in self.purchase_id.order_line - self.confirm_line_ids.mapped('purchase_line_id')-purchase_lines:
            data = self._prepare_confirm_line_from_po_line(line)
            new_line = new_lines.new(data)
            new_lines += new_line

        self.confirm_line_ids += new_lines
        self.purchase_id = False
        return {}

    @api.onchange('category_id')
    def load_products_category_wise(self):
        line_obj = self.env['confirm.window.line']
        self.confirm_line_ids = [(5, _, _)]
        if not self.category_id:
            return
        pd_list = []
        query = '''select pt.list_price,pp.id as product_id,pt.id as template_id,pt.landing_cost,
            pt.product_mrp,pt.margin,pt.margin_per,pp.margin_discount,pp.margin_discount_per
            from product_product as pp
            left join product_template as pt
            on pp.product_tmpl_id = pt.id
            where pt.categ_id = %s and pt.company_id =%s 
                    '''

        self.env.cr.execute(query, (self.category_id.id, self.company_id.id))
        for row in self.env.cr.dictfetchall():
            margin = 0
            new_price = row['list_price'] if row['list_price'] else 0
            margin_per = 0
            if row['product_mrp'] and row['landing_cost']:
                margin = row['product_mrp'] - row['landing_cost']
                margin_per = (margin/row['product_mrp'])*100
            # # if not row['margin'] and margin:
            if row['product_mrp'] and self.mrp_check == True:
                if self.category_id.margin_discount_per:
                    new_price = row['product_mrp']-((margin*self.category_id.margin_discount_per)/100)
                if self.category_id.margin_discount:
                    new_price = row['product_mrp'] - self.category_id.margin_discount
            if row['landing_cost'] and self.mrp_check == False:

                if self.category_id.profit_perc:
                    new_price = (row['landing_cost'] * ((100 + self.category_id.profit_perc) / 100))
                if self.category_id.profit:
                    new_price = row['landing_cost'] + self.category_id.profit
            product_id=self.env['product.product'].browse(row['product_id'])

            values = {
                'product_id': row['product_id'],
                'barcode': True if product_id.barcode_ids else False,
                'article' : row['product_id'],
                'product_tmpl_id':row['template_id'],
                'landing_cost': row['landing_cost'] if row['landing_cost'] else 0,
                'mrp': row['product_mrp'] if row['product_mrp'] else 0,
                'current_price': row['list_price'] if row['list_price'] else 0,
                'new_price':new_price,
                'mrp_check':True if self.mrp_check == True else False,
                'margin': margin,
                'margin_per':margin_per,
                'margin_discount': self.category_id.margin_discount if self.category_id.margin_discount else 0,
                'margin_discount_per': self.category_id.margin_discount_per if self.category_id.margin_discount_per else 0,
                'profit': self.category_id.profit if self.category_id.profit else 0,
                'profit_percentage' : self.category_id.profit_perc if self.category_id.profit_perc else 0

            }
            pd_list.append((0, 0, values))

        self.update({'confirm_line_ids': pd_list,
                                 })

    @api.onchange('filter_date','type')
    def load_products_landing_wise(self):

        self.confirm_line_ids = [(5, _, _)]
        if not self.filter_date:
            return
        pd_list = []

        if self.type == 'landed_cost':


            query = ''' select * from (select pol.product_id,pp.product_tmpl_id,sm.id,pt.list_price,pol.landing_cost,
                    pol.product_mrp,pol.margin,pol.margin_per,pol.sale_price,
                    pol.margin_discount,pol.margin_discount_per,pol.multi_barcode,
                    row_number() over(partition by sm.product_id order by sm.id desc) as rn
                     from stock_move as sm
                    left join stock_picking as sp on sm.picking_id=sp.id
                    left join purchase_order_line as pol on pol.id=sm.purchase_line_id
                    left join product_product as pp on pp.id = pol.product_id
                    left join product_template as pt on pt.id=pp.product_tmpl_id
                    left join product_barcode as pb on pb.product_tmpl_id = pt.id
                    where sp.state='done' and sm.purchase_line_id is not null and pol.landing_cost != pol.old_cost and sm.company_id =%s
                    and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date = %s
                    and pol.multi_barcode is NULL
                    and pol.sale_price != pt.list_price
                    order by pt.name
                    ) t
                    where t.rn = 1 
                                '''
            query2 = ''' select * from (select pol.product_id,pp.product_tmpl_id,sm.id,pb.list_price,pol.landing_cost,
                    pol.product_mrp,pol.margin,pol.margin_per,pol.sale_price,
                    pol.margin_discount,pol.margin_discount_per,pol.multi_barcode,
                    row_number() over(partition by pol.multi_barcode order by sm.id desc) as rn
                     from stock_move as sm
                    left join stock_picking as sp on sm.picking_id=sp.id
                    left join purchase_order_line as pol on pol.id=sm.purchase_line_id
                    left join product_product as pp on pp.id = pol.product_id
                    left join product_template as pt on pt.id=pp.product_tmpl_id
                    left join product_barcode as pb on pb.product_tmpl_id = pt.id
                    where sp.state='done' and sm.purchase_line_id is not null and pol.landing_cost != pol.old_cost and sm.company_id =%s
                    and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date = %s
                    and pol.multi_barcode is NOT NULL
                    and pol.sale_price != pb.list_price
                    order by pt.name
                    ) t
                    where t.rn = 1 

                                            '''
        if self.type == 'sale_price':
            query = '''select * from (select pol.product_id,pp.product_tmpl_id,pt.list_price,pol.landing_cost,
                    pol.product_mrp,pol.margin,pol.margin_per,pol.sale_price,
                    pol.margin_discount,pol.margin_discount_per,pol.multi_barcode,
                    row_number() over(partition by pol.product_id order by pol.id desc) as rn
                     from 
                    purchase_order_line as pol 
                     left join purchase_order as po on po.id=pol.order_id
                    left join product_product as pp on pp.id = pol.product_id
                    left join product_template as pt on pt.id=pp.product_tmpl_id
                    left join product_barcode as pb on pb.product_tmpl_id = pt.id
                    where po.state in ('purchase','done') and pol.sale_price != pt.list_price and pol.company_id = %s
                    and to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date = %s
                    and pol.multi_barcode is NULL
                    and pol.sale_price != pt.list_price
                    order by pt.name
                    ) t
                    where t.rn = 1'''
            query2 = '''select * from (select pol.product_id,pp.product_tmpl_id,pb.list_price,pol.landing_cost,
                    pol.product_mrp,pol.margin,pol.margin_per,pol.sale_price,
                    pol.margin_discount,pol.margin_discount_per,pol.multi_barcode,
                    row_number() over(partition by pol.multi_barcode order by pol.id desc) as rn
                     from purchase_order_line as pol 
                     left join purchase_order as po on po.id=pol.order_id
                    left join product_product as pp on pp.id = pol.product_id
                    left join product_template as pt on pt.id=pp.product_tmpl_id
                    left join product_barcode as pb on pb.product_tmpl_id = pt.id
                    where po.state in ('purchase','done') and pol.sale_price != pb.list_price  and po.company_id = %s
                    and to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date = %s
                    and pol.multi_barcode is NOT NULL
                    and pol.sale_price != pb.list_price
                    order by pt.name
                    ) t
                    where t.rn = 1 '''
        self.env.cr.execute(query2, (self.company_id.id, self.filter_date))
        for row in self.env.cr.dictfetchall():
            values = {
                'product_id': row['product_id'],
                'article': row['product_id'],
                'product_tmpl_id': row['product_tmpl_id'],
                'landing_cost': row['landing_cost'] if row['landing_cost'] else 0,
                'mrp': row['product_mrp'] if row['product_mrp'] else 0,
                'current_price': row['list_price'] if row['list_price'] else 0,
                'new_price': row['sale_price'] if row['sale_price'] else 0,
                'mrp_check': True,
                'margin': row['margin'] if row['margin'] else 0,
                'margin_per': row['margin_per'] if row['margin_per'] else 0,
                'margin_discount': row['margin_discount'] if row['margin_discount'] else 0,
                'margin_discount_per': row['margin_discount_per'] if row['margin_discount_per'] else 0,
                'multi_barcode': row['multi_barcode'] if row['multi_barcode'] else False,

            }
            pd_list.append((0, 0, values))

        self.env.cr.execute(query, (self.company_id.id,self.filter_date ))
        for row in self.env.cr.dictfetchall():


            values = {
                'product_id': row['product_id'],
                'article': row['product_id'],
                'product_tmpl_id': row['product_tmpl_id'],
                'landing_cost': row['landing_cost'] if row['landing_cost'] else 0,
                'mrp': row['product_mrp'] if row['product_mrp'] else 0,
                'current_price': row['list_price'] if row['list_price'] else 0,
                'new_price':row['sale_price'] if row['sale_price'] else 0,
                'mrp_check':True,
                'margin': row['margin'] if row['margin'] else 0,
                'margin_per': row['margin_per'] if row['margin_per'] else 0,
                'margin_discount': row['margin_discount'] if row['margin_discount'] else 0,
                'margin_discount_per': row['margin_discount_per'] if row['margin_discount_per'] else 0,
                'multi_barcode':row['multi_barcode'] if row['multi_barcode'] else False,

            }
            pd_list.append((0, 0, values))





        self.update({'confirm_line_ids': pd_list,
                     })

    @api.multi
    @api.onchange('type')
    def delete_previous_value(self):

        for record in self:

            if record.type == 'product':
                res = {
                    'category_id': False,
                    'margin_discount': False,
                    'margin_discount_per': False,
                    'confirm_line_ids': False,
                    'filter_date': False,
                    'purchase_id':False

                }
                record.update(res)
            if record.type == 'category':
                res = {
                    'filter_date': False,
                    'article': False,
                    'barcode': False,
                    'confirm_line_ids': False,
                    'purchase_id': False

                }
                record.update(res)
            if record.type in ('landed_cost','sale_price'):
                res = {
                    'category_id': False,
                    'margin_discount': False,
                    'margin_discount_per': False,
                    'article': False,
                    'barcode': False,
                    'confirm_line_ids': False,
                    'mrp_check':True,
                    'purchase_id': False
                }
                record.update(res)
            if record.type == 'po':
                res = {
                    'category_id': False,
                    'margin_discount': False,
                    'margin_discount_per': False,
                    'confirm_line_ids': False,
                    'filter_date': False,
                    'article': False,
                    'barcode': False,
                    'mrp_check': True,
                }
                record.update(res)

    @api.multi
    def write(self, values):
        res=super(ConfirmWindow, self).write(values)
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('confirm.window') or '/'
        return super(ConfirmWindow, self).create(vals)

    @api.multi
    def button_confirm(self):

        for rec in self:
            zero_price = [x.product_id.name for x in rec.confirm_line_ids if x.new_price < x.current_price]
            pdct_zero_price = [x.product_id.name for x in rec.confirm_line_ids if x.new_price ==0]
            margin_check = [x.product_id.name for x in rec.confirm_line_ids if x.margin_per<0]
            if zero_price or pdct_zero_price or margin_check:
            	message ="\n"
                if len(zero_price) > 1:
                    message += _(
                        "The following products Price is less than the previous price:") + '\n\n'
                    message += '\n'.join(map(str, zero_price))

                if len(zero_price) == 1:
                    message += _(
                        "The following product Price is less than the previous price:") + '\n\n'
                    message += '\n'.join(map(str, zero_price))


                if len(pdct_zero_price) > 1:
                    message += _(
                        '\n\n'+ "The following products Price is ZERO:") + '\n\n'
                    message += '\n'.join(map(str, pdct_zero_price))

                if len(pdct_zero_price) == 1:
                    message += _(
                        '\n\n'+"The following product Price is ZERO:") + '\n\n'
                    message += '\n'.join(map(str, pdct_zero_price))

                if len(margin_check) > 1:
                    message += _(
                       '\n\n'+ "The following products Margin Percentage is negative:") + '\n\n'
                    message += '\n'.join(map(str, margin_check))

                if len(margin_check) == 1:
                    message += _(
                        '\n\n'+"The following product Margin Percentage is negative:") + '\n\n'
                    message += '\n'.join(map(str, margin_check))
                message += '\n\nAre you sure you want to confirm this?'

                query = 'delete from product_confirm_cancel_window'
                rec.env.cr.execute(query)
                value = rec.env['product.confirm.cancel.window'].sudo().create({'text_message': message})
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Do you Want to Continue',
                    'res_model': 'product.confirm.cancel.window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'confirm_obj': rec.id, },
                    'res_id': value.id
                }
            else:
                rec.change_retail_price()

    @api.multi
    def change_retail_price(self):
        for rec in self:
            if rec.mrp_check == True:
                for line in rec.confirm_line_ids:

                    if line.multi_barcode:
                        line.multi_barcode.update({'new_price':line.new_price,
                                                   'margin':line.margin,
                                                   'product_mrp':line.mrp if rec.type in ('category','product') else line.multi_barcode.product_mrp,
                                                   'margin_per': line.margin_per,
                                                   'margin_discount':line.margin_discount,
                                                   'margin_discount_per':line.margin_discount_per})
                    else:
                        line.product_id.update({'new_price':line.new_price,
                                                'margin': line.margin,
                                                'product_mrp': line.mrp if rec.type in ('category','product') else line.product_id.product_mrp,
                                                'margin_per': line.margin_per,
                                                'margin_discount': line.margin_discount,
                                                'margin_discount_per': line.margin_discount_per
                                                })
            else:
                for line in rec.confirm_line_ids:

                    if line.multi_barcode:
                        line.multi_barcode.update({
                            'new_price':line.new_price,
                            'product_mrp': line.mrp if rec.type in (
                                    'category', 'product') else line.multi_barcode.product_mrp,
                            'profit':line.profit,
                            'profit_perc':line.profit_percentage})
                    else:
                        line.product_id.update({'new_price':line.new_price,
                                                'product_mrp': line.mrp if rec.type in (
                                                'category', 'product') else line.product_id.product_mrp,
                                                'profit': line.profit,
                                                'profit_perc': line.profit_percentage
                                                })

            rec.write({'state': 'confirm'})

    @api.multi
    def button_update(self):
        for rec in self:
            for line in rec.confirm_line_ids:
                if line.multi_barcode:
                    line.multi_barcode.update({'list_price':line.new_price})
                else:
                    line.product_id.update({'lst_price':line.new_price})
            rec.write({'state': 'update'})
    @api.multi
    def button_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ['confirm', 'update']:
                raise UserError(_('Cannot delete a record which is in state \'%s\'.') % (rec.state,))

        return super(ConfirmWindow, self).unlink()

    @api.onchange('article')
    def load_product_based_article(self):

        if not self.article:
            return {}
        product_details = {}
        product_id = self.env['product.product'].browse(self.article)
        if not product_id:
            self.article = False
            return {

                'warning': {'title': 'Error!', 'message': 'Please enter the correct article number'},
                'value': {
                    'article': False,

                }
            }

        order_line_var = self.env['confirm.window.line']
        margin = 0
        margin_per = 0
        if product_id.product_mrp and product_id.landing_cost:
            margin = product_id.product_mrp - product_id.landing_cost
            margin_per = (margin/product_id.product_mrp)*100
        values = {
            'article':product_id.id,
            'product_id': product_id.id,
            'current_price': product_id.lst_price,
            'landing_cost': product_id.landing_cost,
            'choose_opt': 'sale_price',
            'new_price':product_id.lst_price,
            'barcode': True if product_id.barcode_ids else False,
            'mrp_check': True if self.mrp_check == True else False,
            'mrp': product_id.product_mrp,
            'date':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'margin': margin,
            'margin_per': margin,
            # 'margin_discount': product_id.margin_discount,
            # 'margin_discount_per': product_id.margin_discount_per,
        }

        order_line_var1 = order_line_var.new(values)
        order_line_var += order_line_var1
        self.confirm_line_ids += order_line_var
        self.article = False

    @api.onchange('barcode')
    def onchange_barcode_load_product(self):
        if not self.barcode:
            return {}

        product_id = self.env['product.product'].search([('barcode', '=', self.barcode)])

        if not product_id:
            self.barcode = False

            return {

                'warning': {'title': 'Error!', 'message': 'Please enter the correct barcode'},
                'value': {
                    'barcode': False,

                }
            }

        order_line_var = self.env['confirm.window.line']
        margin = 0
        margin_per = 0
        if product_id.product_mrp and product_id.landing_cost:
            margin = product_id.product_mrp - product_id.landing_cost
            margin_per = (margin/product_id.product_mrp)*100
        values = {
            'article': product_id.id,
            'product_id': product_id.id,
            'current_price': product_id.lst_price,
            'landing_cost': product_id.landing_cost,
            'mrp_check': True if self.mrp_check == True else False,
            'mrp': product_id.product_mrp,
            'choose_opt': 'sale_price',
            'margin': margin,
            'margin_per': margin_per,
            'barcode': True if product_id.barcode_ids else False,
            'new_price': product_id.lst_price,
            # 'margin_discount': product_id.margin_discount,
            # 'margin_discount_per': product_id.margin_discount_per,
            'date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),


        }

        order_line_var1 = order_line_var.new(values)
        order_line_var += order_line_var1
        self.confirm_line_ids += order_line_var
        self.barcode = False

class ConfirmWindowLine(models.Model):
    _name = 'confirm.window.line'

    @api.depends('product_id')
    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.confirm_id.confirm_line_ids:
                line_rec.sl_no = line_num
                line_num += 1



    multi_barcode = fields.Many2one('product.barcode', string="Multi Barcode", )
    confirm_id = fields.Many2one('confirm.window', string='Confirm Reference',
                                 ondelete='cascade', index=True,required=True,copy=False)
    sl_no = fields.Integer(compute='_get_line_numbers', string='Sl No.', readonly=False, store=True)
    article = fields.Integer(string='Article')
    mrp_check = fields.Boolean(string='MRP Products', related='confirm_id.mrp_check', required=True)
    margin_discount = fields.Float(string='Margin Discount', digits=dp.get_precision('Product Price'), default=0)
    margin_discount_per = fields.Float(string='Margin Discount(%)', digits=dp.get_precision('Product Price'),
                                       default=0)
    landing_cost = fields.Float(string="Landing Cost", digits=dp.get_precision('Product Price'), default=0)
    mrp = fields.Float(string="MRP", digits=dp.get_precision('Product Price'), default=0)
    margin = fields.Float('Margin', digits=dp.get_precision('Product Price'), default=0)
    margin_per = fields.Float('Margin %', digits=dp.get_precision('Product Price'), default=0)

    product_id = fields.Many2one('product.product', string='Product',
                                 ondelete='restrict', index=True,)
    product_tmpl_id = fields.Many2one('product.template', string="Product Template",
                                      related='product_id.product_tmpl_id', store=True, )
    # confirm = fields.Boolean(string="confirm",default=False)
    barcode = fields.Boolean(string="barcodes", default=False)
    new_price = fields.Float(string='New Price', required=True, digits=dp.get_precision('Product Price'),default=0,store=True)
    current_price = fields.Float(string='Current Price',  digits=dp.get_precision('Product Price'),default=0,store=True)


    on_hand=fields.Float(string="Onhand",default=0,store=True)

    user_id = fields.Many2one('res.users', string='User',related="confirm_id.user_id")
    date = fields.Date(string='Date', default=fields.Date.context_today, copy=False, store=True )
    company_id = fields.Many2one('res.company', related='confirm_id.company_id', string='Company', store=True,
                                 readonly=True)
    choose_opt = fields.Selection([
            ('sale_price', 'Sale Price'),
            ('margin_per', 'Discount %'),
            ('margin_amt', 'Discount Amt'),
            ('profit_per', 'Profit %'),
            ('profit_amt', 'Profit Amt'),
        ], string='Option', default='sale_price',

    )


    profit = fields.Float(string='Profit', digits=dp.get_precision('Product Price'), default=0)
    profit_percentage = fields.Float('Profit (%)', default=0)

    purchase_line_id = fields.Many2one('purchase.order.line', 'Purchase Order Line', ondelete='set null', index=True,
                                       readonly=True)
    purchase_id = fields.Many2one('purchase.order', related='purchase_line_id.order_id', string='Purchase Order',
                                  store=False, readonly=True, related_sudo=False,
                                  help='Associated Purchase Order. Filled in automatically when a PO is chosen on the vendor bill.')

    @api.multi
    @api.constrains('mrp', 'new_price')
    def _check_mrp_landing_sale_price(self):

        for line in self:

            if line.mrp < line.new_price:
                raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For %s and article %s ")% (line.product_id.name,line.product_id.id))

    @api.onchange('multi_barcode')
    def change_product_values(self):
        for record in self:
            if record.multi_barcode:
                margin = 0
                margin_per = 0
                new_price = record.multi_barcode.list_price if record.confirm_id.type in ('product','category') else 0
                if record.multi_barcode.product_mrp and record.multi_barcode.landing_cost:
                    margin = record.multi_barcode.product_mrp - record.multi_barcode.landing_cost
                    margin_per = (margin/record.multi_barcode.product_mrp)*100
                if record.multi_barcode.product_mrp and record.confirm_id.mrp_check:
                    if record.margin_discount_per:
                        new_price = record.multi_barcode.product_mrp - ((margin * record.margin_discount_per) / 100)
                    if record.margin_discount:
                        new_price = record.multi_barcode.product_mrp - record.margin_discount
                if record.landing_cost and record.confirm_id.mrp_check==False:
                    if record.profit:
                        new_price = record.landing_cost + record.profit
                    if record.profit_percentage:
                        new_price = (record.landing_cost * ((100 + record.profit_percentage) / 100))
                record.update({
                    'landing_cost':record.multi_barcode.landing_cost,
                    'margin':margin,
                    'margin_per': margin_per,
                    'mrp':record.multi_barcode.product_mrp,
                    'new_price':new_price,
                    # 'margin_discount':record.multi_barcode.margin_discount,
                    # 'margin_discount_per':record.multi_barcode.margin_discount_per,
                    'current_price':record.multi_barcode.list_price

                })

            else:
                margin = 0
                margin_per = 0
                new_price = record.product_id.lst_price if record.confirm_id.type in ('product','category') else 0
                if record.product_id.product_mrp and record.product_id.landing_cost:
                    margin = record.product_id.product_mrp - record.product_id.landing_cost
                    margin_per = (margin/record.product_id.product_mrp)*100
                if record.product_id.product_mrp and record.confirm_id.mrp_check==True:
                    if record.margin_discount_per:
                        new_price = record.product_id.product_mrp - ((margin * record.margin_discount_per) / 100)
                    if record.margin_discount:
                        new_price = record.product_id.product_mrp - record.margin_discount
                if record.product_id.landing_cost and record.confirm_id.mrp_check==False:
                    if record.profit:
                        new_price = record.product_id.landing_cost + record.profit
                    if record.profit_percentage:
                        new_price = (record.product_id.landing_cost * ((100 + record.profit_percentage) / 100))
                record.update({
                    'landing_cost': record.product_id.landing_cost,
                    'margin': margin,
                    'margin_per': margin_per,
                    'mrp': record.product_id.product_mrp,
                    'new_price':new_price,
                    # 'margin_discount': record.product_id.margin_discount,
                    # 'margin_discount_per': record.product_id.margin_discount_per,
                    'current_price': record.product_id.lst_price

                })



    @api.model
    def create(self, values):
        line = super(ConfirmWindowLine, self).create(values)
        return line

    @api.multi
    def write(self, values):
        line=super(ConfirmWindowLine, self).write(values)
        return line

    @api.multi
    def unlink(self):
        for line in self:
            if line.confirm_id.state in ['confirm', 'cancel']:
                raise UserError(_('Cannot delete a product line which is in state \'%s\'.') % (line.confirm_id.state,))

        return super(ConfirmWindowLine, self).unlink()




    @api.onchange('product_id')
    def onchange_product_id(self):

        result = {}
        if not self.product_id:
            return result
        margin = 0
        margin_per = 0
        if self.product_id.product_mrp - self.product_id.landing_cost:
            margin = self.product_id.product_mrp - self.product_id.landing_cost
            margin_per = (margin/self.product_id.product_mrp)*100
        self.date = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.current_price = self.product_id.lst_price
        self.landing_cost = self.product_id.landing_cost
        self.mrp = self.product_id.product_mrp
        self.mrp_check =  True if self.confirm_id.mrp_check == True else False
        self.article = self.product_id.id
        self.product_tmpl_id = self.product_id.product_tmpl_id.id
        self.margin = margin
        self.margin_per = margin_per
        self.choose_opt = 'sale_price'
        self.barcode = True if self.product_id.barcode_ids else False
        self.new_price = self.product_id.lst_price if self.confirm_id.type in ('product','category') else 0


    @api.onchange('new_price', 'choose_opt','mrp_check')
    def Calculate_margin_based_price(self):

        for rec in self:

            if rec.choose_opt == 'sale_price' and rec.mrp_check == True:
                discount_amt = 0
                discount_per = 0
                discount_amt = rec.mrp-rec.new_price
                if rec.margin:
                    discount_per = (discount_amt / rec.margin) * 100
                # else:
                #     discount_per = (discount_amt / (rec.mrp-rec.landing_cost) )* 100 if (rec.mrp-rec.landing_cost)>0 else 0
                rec.margin_discount = discount_amt
                rec.margin_discount_per = discount_per
            if rec.choose_opt == 'sale_price' and rec.mrp_check == False:
                discount_amt = 0
                discount_per = 0
                discount_amt = rec.new_price - rec.landing_cost
                discount_per = (rec.new_price - rec.landing_cost-1) * 100
                # else:
                #     discount_per = (discount_amt / (rec.mrp-rec.landing_cost) )* 100 if (rec.mrp-rec.landing_cost)>0 else 0
                rec.profit = discount_amt
                rec.profit_percentage = discount_per


    @api.onchange('margin_discount', 'choose_opt','mrp_check')
    def Calculate_price_based_discount(self):
        for rec in self:
            new_price = 0
            discount_per = 0

            if rec.choose_opt == 'margin_amt' and rec.mrp_check == True:

                new_price = rec.mrp-rec.margin_discount
                if rec.margin:
                    discount_per = (rec.margin_discount / rec.margin) * 100
                # else:
                #     discount_per = (rec.margin_discount / (rec.mrp - rec.landing_cost)) * 100 if (rec.mrp - rec.landing_cost) > 0 else 0

                rec.new_price = new_price
                rec.margin_discount_per = discount_per



    @api.onchange('margin_discount_per', 'choose_opt','mrp_check')
    def Calculate_price_based_gpper(self):
        for rec in self:

            if rec.choose_opt == 'margin_per' and rec.mrp_check == True:
                discount_amt = 0
                new_price = 0
                if rec.margin:
                    discount_amt = (rec.margin_discount_per * rec.margin) / 100
                # else:
                #     discount_amt = (rec.margin_discount_per * (rec.mrp-rec.landing_cost)) / 100 if (rec.mrp-rec.landing_cost)>0 else 0
                new_price = rec.mrp - discount_amt

                rec.margin_discount = discount_amt
                rec.new_price = new_price





    @api.onchange('profit', 'choose_opt', 'mrp_check')
    def Calculate_price_based_profit(self):
        for rec in self:
            new_price = 0
            discount_per = 0

            if rec.choose_opt == 'profit_amt' and rec.mrp_check == False:

                new_price = rec.profit+rec.landing_cost
                discount_per = (new_price - rec.landing_cost-1) * 100
                # else:
                #     discount_per = (rec.margin_discount / (rec.mrp - rec.landing_cost)) * 100 if (rec.mrp - rec.landing_cost) > 0 else 0

                rec.new_price = new_price
                rec.profit_percentage = discount_per

    @api.onchange('profit_percentage', 'choose_opt', 'mrp_check')
    def Calculate_price_based_profit_percentage(self):
        for rec in self:

            if rec.choose_opt == 'profit_per' and rec.mrp_check == False:
                discount_amt = 0
                new_price = 0
                new_price = (rec.landing_cost * ((100 + rec.profit_percentage) / 100))
                discount_amt = new_price-rec.landing_cost
                # else:
                #     discount_amt = (rec.margin_discount_per * (rec.mrp-rec.landing_cost)) / 100 if (rec.mrp-rec.landing_cost)>0 else 0


                rec.profit = discount_amt
                rec.new_price = new_price

class ProductCancelWindow(models.Model):
    _name = 'product.confirm.cancel.window'

    text_message=fields.Text()


    def confirm_product_price(self):
        if self.env.context['confirm_obj']:
            confirm_obj=self.env['confirm.window'].browse(self.env.context['confirm_obj'])

            for rec in confirm_obj:

                rec.change_retail_price()

            pass