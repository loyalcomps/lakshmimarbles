from odoo import models, fields, api,_


class ProductSp(models.TransientModel):
    _name = 'product.sp'

    category_id = fields.Many2one('product.category',string="Category")
    discount = fields.Float(string="Discount",readonly=True,store=True)

    @api.onchange('category_id')
    def onchange_category(self):
        self.update({'discount': self.category_id.discount})
        line_obj = self.env['product.sp.line']
        self.product_line=[(5, _, _)]
        if not self.category_id:
            return

        query = '''select p.id as id,t.categ_id as categ_id,COALESCE(t.landing_cost, 0) as landing_cost,COALESCE(p.product_mrp, 0) as product_mrp from product_template t left join product_product p on (t.id = p.product_tmpl_id) 
where t.categ_id = %s order by t.name'''

        self.env.cr.execute(query,(self.category_id.id,))

        for row in self.env.cr.dictfetchall():

            margin = (row['product_mrp'] - row['landing_cost']) if (row['product_mrp'] - row['landing_cost']) > 0 else 0
            list_price = (row['product_mrp'] - (((margin) * self.discount) / 100))

            values = {
                'product_id':row['id'],
                'mrp':row['product_mrp'],
                'cost':row['landing_cost'],
                'sale_price':list_price

            }

            order_line_var1 = line_obj.new(values)
            # line_obj += order_line_var1
            self.product_line += order_line_var1




        # products=self.env['product.product'].search([('categ_id', '=', self.category_id.id)])
        # for product in products:
        #     for pr in product:
        #         cost = 0
        #         invoice = self.env['account.invoice.line'].search([('product_id', '=', pr.id)], order='id desc',
        #                                                           limit=1)
        #
        #         if pr.landing_cost:
        #             cost = pr.landing_cost
        #         else:
        #             for product in invoice:
        #                 if product.quantity != 0:
        #                     cost = (product.price_subtotal_taxinc / product.quantity)
        #
        #         # pr.margin = pr.product_mrp - cost
        #         margin = (pr.product_mrp-cost)if (pr.product_mrp-cost) >0 else 0
        #         list_price = (pr.product_mrp - (((margin) * self.discount) / 100))
        #         # pr.list_price = list_price
        #         values={
        #             'product_id':pr.id,
        #             'mrp':pr.product_mrp,
        #             'cost':pr.landing_cost,
        #             'sale_price':list_price
        #
        #         }
        #
        #         order_line_var1 = line_obj.new(values)
        #         # line_obj += order_line_var1
        #         self.product_line += order_line_var1


    # type = fields.Selection([('all','All'),('specific','Specific')],string='Set to',default="all")
    product_line = fields.One2many('product.sp.line','product_price_id',string="Products")

    @api.multi
    def change_product_price(self):

        for record in self.product_line:
            record.product_id.lst_price=record.sale_price
            # record.product


        # if self.type=="all":
        #     categories = self.env['product.category'].search([])
        #     for category in categories:
        #         products = self.env['product.product'].search([('categ_id','=',category.id)])
        #         for record in products:
        #             for pr in record:
        #                 cost = 0
        #                 invoice = self.env['account.invoice.line'].search([('product_id', '=', pr.id)],order='id desc',limit=1)
        #
        #                 if pr.standard_price:
        #                     cost = pr.standard_price
        #                 else:
        #                     for product in invoice:
        #                         if product.quantity != 0:
        #                             cost = (product.price_subtotal_taxinc / product.quantity)
        #
        #
        #                 pr.margin = pr.product_mrp - cost
        #                 pr.list_price = (pr.product_mrp - (((pr.product_mrp - cost) * category.discount) / 100))
        #
        # else:
        #     for line in self.product_line:
        #         categories = self.env['product.category'].search([('id', '=', line.category_id.id)])
        #         for category in categories:
        #             products = self.env['product.product'].search([('categ_id', '=', category.id)])
        #             for record in products:
        #                 for pr in record:
        #                     cost = 0
        #                     invoice = self.env['account.invoice.line'].search([('product_id', '=', pr.id)], order='id desc',
        #                                                           limit=1)
        #
        #                     if pr.standard_price:
        #                         cost = pr.standard_price
        #                     else:
        #                         for product in invoice:
        #                             if product.quantity != 0:
        #                                 cost = (product.price_subtotal_taxinc / product.quantity)
        #
        #                     pr.margin = pr.product_mrp - cost
        #                     pr.list_price = (pr.product_mrp - (((pr.product_mrp - cost) * line.discount) / 100))


class ProductSpLine(models.TransientModel):
    _name = 'product.sp.line'

    product_id = fields.Many2one('product.product',string="Product")
    mrp = fields.Float(string='MRP', default='0.0')
    cost = fields.Float(string='Cost',default='0.0')
    sale_price = fields.Float(string='Sale Price',default='0.0')

    product_price_id = fields.Many2one('product.sp')


    # category_id = fields.Many2one('product.category', string="Category", required=True)
    # discount = fields.Float(string="Discount(%)", default="0.0")


    # @api.onchange('category_id')
    # def get_category(self):
    #     cat_obj = self.env['product.category'].search([('id', '=', self.category_id.id)])
    #     self.discount = cat_obj.discount




class ProductCategory(models.Model):
    _inherit = 'product.category'

    discount = fields.Float(string="Discount(%)", default="0.0")

