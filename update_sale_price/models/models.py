# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class update_sale_price(models.TransientModel):
    _name = 'update.sale.price'
    _description = 'Updating sales price'

    type = fields.Selection([('category', 'Category'), ('product', 'Product')], string='Type', default="category",required=True)
    category_id = fields.Many2one('product.category', string='Category')
    product_id = fields.Many2one('product.product', string='Product')
    margin_discount = fields.Float(string='Margin Discount',digits=dp.get_precision('Margin Discount'),default=0)
    margin_discount_per = fields.Float(string='Margin Discount(%)', digits=dp.get_precision('Margin Discount'),default=0)
    landing_cost = fields.Float(string="Landing Cost",digits=dp.get_precision('Product Price'),default=0)
    mrp = fields.Float(string="MRP", digits=dp.get_precision('Product Price'),default=0)
    sell_price = fields.Float(string="Sell price", digits=dp.get_precision('Product Price'),default=0)
    # sale_price = fields.Float(string="Sale price",default=0)
    mrp_check = fields.Boolean(string='MRP Products',default=True,required=True)
    margin = fields.Float('Margin', digits=dp.get_precision('Product Price'),default=0)
    # margin_percentage = fields.Float('Margin (%)', default=0)
    profit = fields.Float(string='Profit',digits=dp.get_precision('Product Price'),default=0)
    profit_percentage = fields.Float('Profit (%)', default=0)
    update_sale_price_line_ids = fields.One2many('update.sale.price.line', 'update_sale_price_id', string="Products")
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env['res.company']._company_default_get('update.sale.price'))

    @api.multi
    @api.onchange('mrp_check')
    def filter_product_id(self):
        li = []
        res = {}
        if self.type == 'product':
            res = {
                'product_id': False,
                'margin_discount': False,
                'margin_discount_per': False,
                'profit': False,
                'profit_percentage': False,
                'landing_cost': False,
                'sell_price': False,
                'mrp': False,
                'margin': False,
                # 'margin_percentage': False
            }
            self.update(res)
        if self.mrp_check is True:

            res['domain'] = {'product_id': [('product_mrp', '!=', 0)]}
        else:
            query = '''select pp.id
                        from product_product as pp
                        left join product_template as pt
                        on pp.product_tmpl_id = pt.id
                        where  pt.company_id = %s and (pt.product_mrp = 0 or pt.product_mrp is null)
                            '''
            self.env.cr.execute(query, (self.company_id.id,))
            for row in self.env.cr.dictfetchall():
                li.append(row['id'])
            res['domain'] = {'product_id': [('id', 'in', li)]}
            # res['domain'] = {'product_id': [('product_mrp', '=', 0)]}
        return res

    @api.multi
    @api.onchange('type')
    def delete_previous_value(self):

        for record in self:
            if record.type == 'product':
                res = {
                    'category_id': False,
                    'margin_discount': False,
                    'margin_discount_per': False,
                    'profit': False,
                    'profit_percentage': False
                }
                record.update(res)
            if record.type == 'category':
                res = {
                    'product_id': False,
                    'margin_discount': False,
                    'margin_discount_per': False,
                    'profit': False,
                    'profit_percentage': False,
                    'landing_cost': False,
                    'sell_price': False,
                    'mrp': False,
                    'margin': False,
                    # 'margin_percentage': False
                }
                record.update(res)

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {'landing_cost': self.product_id.landing_cost,
               'mrp': self.product_id.product_mrp,
               'margin': self.product_id.margin,
               # 'margin_percentage': self.product_id.margin_percentage,
               'sell_price': self.product_id.lst_price,
        }
        self.update(res)
        # self.sale_price = self.product_id.lst_price

    @api.onchange('sell_price', 'mrp', 'landing_cost')
    def compute_margin(self):
        for record in self:
            if record.mrp:
                record.margin = record.mrp - record.landing_cost
                # record.list_price = record.product_mrp - ((record.margin*record.margin_discount_percentage)/100)
            if not record.mrp:
                record.margin = (record.landing_cost*record.margin_discount_per)/100
                # record.list_price = record.landing_cost + record.margin
            # record.margin = record.mrp - record.landing_cost
            # if record.mrp:
            #     # record.margin_percentage = (record.mrp - record.landing_cost) * 100 / record.mrp
            # if not record.mrp:
            #     record.margin = record.sell_price - record.landing_cost
            #     if record.sell_price:
            #         # record.margin_percentage = (record.sell_price - record.landing_cost) * 100 / record.sell_price

    @api.multi
    @api.onchange('margin_discount', 'margin_discount_per')
    def onchange_margin(self):


        for record in self:
            # sell_price = record.sale_price
            if record.type == 'category':

                for line in record.update_sale_price_line_ids:

                    sell_price = line.price

                    if line.margin:
                        if record.margin_discount:
                            sell_price = line.landing_cost + line.margin - record.margin_discount
                        if record.margin_discount_per:
                            sell_price = line.landing_cost + (
                                    line.margin * ((100 - record.margin_discount_per) / 100))
                    if not line.margin and line.mrp:
                        if not line.sell_price:
                            sell_price = line.mrp
                        else:
                            sell_price = line.sell_price

                    res = {
                            'margin_discount': record.margin_discount,
                            'margin_discount_per': record.margin_discount_per,
                            'sell_price': sell_price

                        }
                    line.update(res)
                    # line.margin_discount = record.margin_discount
                    # line.margin_discount_per = record.margin_discount_per
            if record.type == 'product':
                if record.margin:
                    if record.margin_discount:
                        record.sell_price = record.landing_cost+record.margin-record.margin_discount
                    if record.margin_discount_per:
                        record.sell_price = record.landing_cost + (record.margin*((100-record.margin_discount_per)/100))
                if not record.margin and record.mrp:
                    if not record.sell_price:
                        record.sell_price = record.mrp
                    else:
                        record.sell_price = record.sell_price


    @api.multi
    @api.onchange('profit', 'profit_percentage')
    def onchange_profit(self):
        for record in self:
            sell_price = 0
            if record.type == 'category':
                for line in record.update_sale_price_line_ids:

                    if record.profit:
                        sell_price = line.landing_cost + record.profit
                    if record.profit_percentage:
                        sell_price = (line.landing_cost * ((100 + record.profit_percentage) / 100))
                    res = {
                        'profit': record.profit,
                        'profit_percentage': record.profit_percentage,
                        'sell_price':sell_price
                    }
                    line.update(res)
                    # line.margin_discount = record.margin_discount
                    # line.margin_discount_per = record.margin_discount_per
            if record.type == 'product':
                if record.profit:
                    record.sell_price = record.landing_cost + record.profit
                if record.profit_percentage:
                    record.sell_price = (record.landing_cost * ((100 + record.profit_percentage) / 100))

    @api.onchange('category_id', 'mrp_check')
    def load_products(self):
        line_obj = self.env['update.sale.price.line']
        self.update_sale_price_line_ids = [(5, _, _)]
        if not self.category_id:
            return

        if self.mrp_check == True:
            query = '''select pt.list_price,pp.id,pt.landing_cost,pt.product_mrp,pp.margin,pt.margin_discount,pt.margin_discount_perc
                    from product_product as pp
                    left join product_template as pt
                    on pp.product_tmpl_id = pt.id
                    where pt.categ_id = %s and pt.company_id = %s and pt.product_mrp <> 0
                '''
        if self.mrp_check == False:
            query = '''select pt.list_price,pp.id,pt.landing_cost,pt.product_mrp,pp.margin,pt.margin_discount,pt.margin_discount_perc
                    from product_product as pp
                    left join product_template as pt
                    on pp.product_tmpl_id = pt.id
                    where pt.categ_id = %s and pt.company_id = %s and (pt.product_mrp = 0 or pt.product_mrp is null)
                '''
        self.env.cr.execute(query, (self.category_id.id,self.company_id.id))
        for row in self.env.cr.dictfetchall():
            margin=0
            if row['product_mrp'] and row['landing_cost']:
              margin = row['product_mrp'] - row['landing_cost']
            # if not row['margin'] and margin:

            values = {
                'product_id': row['id'],
                'sell_price': row['list_price'] if row['list_price'] else 0,
                'price': row['list_price'] if row['list_price'] else 0,
                'landing_cost': row['landing_cost'] if row['landing_cost'] else 0,
                'mrp': row['product_mrp'] if row['product_mrp'] else 0,
                # 'margin': row['margin'] if row['margin'] else 0,
                'margin':margin,
                'margin_discount':row['margin_discount'],
                'margin_discount_per': row['margin_discount_perc']
                # 'margin_percentage': row['margin_percentage'] if row['margin_percentage'] else 0,
            }

            # product = self.env['product.product'].search([('id', '=', row['id'])])
            # print 'PRODUCT:',product.id
            # product.update({'margin': margin})
            # print 'PRODUCT-MARGIN',product.margin
            order_line_var1 = line_obj.new(values)
            # print 'SALE PRICE:',values['sale_price']
            self.update_sale_price_line_ids += order_line_var1


    @api.multi
    def update_sell_price(self):
        if not self.category_id:
            raise ValidationError('Please select category')
        if self.mrp_check:
           if not self.margin_discount and not self.margin_discount_per:
              raise ValidationError('Please select margin discount or margin discout percentage')
        if not self.mrp_check:
           if not self.profit and not self.profit_percentage:
                raise ValidationError('Please select profit or profit percentage')
        for record in self:
            if record.type == 'product':
                if record.product_id:
                    product = self.env['product.product'].search([('id','=',record.product_id.id)])
                    res = {
                        # 'landing_cost': record.landing_cost,
                        # 'product_mrp': record.mrp,
                        'margin': record.margin,
                        # 'margin_percentage': record.margin_percentage,
                        'lst_price': record.sell_price
                        # 'margin_discount_perc':record.margin_discount_perc
                    }
                    product.update(res)
                    # record.product_id.product_tmpl_id.margin_discount_perc = record.margin_discount_per

            if record.type == 'category':
                for sp in record.update_sale_price_line_ids:
                    sp.product_id.lst_price = sp.sell_price
                    # sp.product_id.lst_price = sp.sell_price
                    sp.product_id.margin = sp.margin
                    sp.product_id.margin_discount_perc = sp.margin_discount_per
                    sp.product_id.margin_discount = sp.margin_discount

        # category = self.env['product.category'].search([('id', '=', self.category_id)])
        if self.category_id:
           if self.mrp_check:
              self.category_id.margin_discount_perc = self.margin_discount_per
              self.category_id.margin_discount = self.margin_discount
           if not self.mrp_check:
              self.category_id.profit=self.profit
              self.category_id.profit_perc = self.profit_percentage

           # code for pop-up
           view = self.env.ref('sh_message.sh_message_wizard')
           view_id = view and view.id or False
           context = dict(self._context or {})
           context['message']="Sale price updated successfully"
           return{
               'name':'Success',
               'type':'ir.actions.act_window',
               'view_type':'form',
               'view_mode':'form',
               'res_model':'sh.message.wizard',
               'views':[(view.id,'form')],
               'view_id':view.id,
               'target':'new',
               'context':context,
            }

        # return
class UpdateSalePriceLine(models.TransientModel):
    _name = 'update.sale.price.line'

    sl_no = fields.Integer(string='Sl No.',readonly=False,store=True,compute='_get_line_numbers')
    product_id = fields.Many2one('product.product', string="Product", required=True)
    margin_discount = fields.Float(string='Margin Discount', digits=dp.get_precision('Margin Discount'), default=0)
    margin_discount_per = fields.Float(string='Margin Discount(%)', digits=dp.get_precision('Margin Discount'),default=0)
    landing_cost = fields.Float(string="Landing Cost", digits=dp.get_precision('Product Price'), default=0)
    mrp = fields.Float(string="MRP", digits=dp.get_precision('Product Price'), default=0)
    sell_price = fields.Float(string="Sell price", digits=dp.get_precision('Product Price'), default=0)
    price = fields.Float(store=True)
    margin = fields.Float('Margin', digits=dp.get_precision('Product Price'), default=0)
    # margin_percentage = fields.Float('Margin (%)', default=0)
    profit = fields.Float(string='Profit', digits=dp.get_precision('Product Price'), default=0)
    profit_percentage = fields.Float('Profit (%)', default=0)
    mrp_check = fields.Boolean(string='MRP Products', related='update_sale_price_id.mrp_check', required=True)

    update_sale_price_id = fields.Many2one('update.sale.price', string="Update Sale Price", )

    @api.depends('product_id')
    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.update_sale_price_id.update_sale_price_line_ids:
                line_rec.sl_no = line_num
                line_num += 1

    @api.multi
    @api.onchange('profit', 'profit_percentage','margin_discount','margin_discount_per')
    def calculate_sell_price(self):
        for record in self:
            if record.mrp_check == True:
                if record.margin:
                    if record.margin_discount:

                        record.sell_price = record.landing_cost+record.margin-record.margin_discount
                    if record.margin_discount_per:
                        record.sell_price = record.landing_cost + (record.margin*((100-record.margin_discount_per)/100))
                if not record.margin and record.mrp:
                    if not record.sell_price:
                        record.sell_price = record.mrp
                    else:
                        record.sell_price = record.sell_price

            else:
                if record.profit:
                    record.sell_price = record.landing_cost + record.profit
                if record.profit_percentage:
                    record.sell_price = (record.landing_cost * ((100 + record.profit_percentage) / 100))


