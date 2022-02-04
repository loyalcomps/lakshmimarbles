from odoo import models, fields, api


class ParentCategory(models.TransientModel):
    _name = "parent.category.pdf"
    _description = "category wise report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    cat_only = fields.Boolean(string='All Category')
    subcategory_id= fields.Many2one('product.category',string='Category')

    stock_location = fields.Many2one('stock.location',required=True,
                                     string='Select Location',domain= [('usage','=','internal')])

    def parent_category(self):
        a = []

        qry='''

    select distinct(parent_id) as id
    from product_category where parent_id is not null


    '''

        self.env.cr.execute(qry, ())
        for row1 in self.env.cr.dictfetchall():
            # self.category_id = (row1['id'] if row1['id'] else 0)

            # a.append(row1['id'])
            res = {
                'id': row1['id'],

            }

            a.append(row1['id'])
        qry2 = '''

            select id,name from product_category where parent_id is null


            '''

        self.env.cr.execute(qry2, ())
        for row1 in self.env.cr.dictfetchall():

            if id not in a:
                a.append(row1['id'])

        if a:
            return [('id','in',a)]
        else:
            return []



    # company_id = fields.Many2one('res.company', required=True,string='Select Company',default=lambda self: self.env.user.company_id.id)
    category_id= fields.Many2one('product.category',string='Parent Category',domain=parent_category)

    child_category = fields.Many2many('product.category', string='Child Category',

                                      domain="[('id','child_of',category_id)]")

    @api.onchange('category_id')
    def onchange_type_category_id(self):
        self.child_category=False



    # @api.onchange('category_id')
    # def onchange_type_category_id(self):
    #     domain = []
    #     if self.category_id:
    #         domain += [('id','child_of',self.category_id.id)]
    #         self.child_category = self.env['product.category'].search(domain)
    #     else:
    #         self.child_category = None
    #



    # child_category= fields.Many2one('product.category',string='Child Category',domain=child_category)





    # domain = "[('product_tmpl_id', '=', product_tmpl_id)]"


    @api.multi
    def export_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sale.order'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]

        return self.env['report'].get_action(
            [], 'parent_category_pdf.parent_category_pdf', data=datas)
