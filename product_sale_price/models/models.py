# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class Product_SP(models.Model):
    _name = 'product.sp'

    partner_id = fields.Many2one('res.partner',string="Vendor",domain=[('supplier','=',True)])
    product_sp_line_ids = fields.One2many('product.sp.line','product_sp_id',string="Products")
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env['res.company']._company_default_get('product.sp'))

    @api.onchange('partner_id')
    def load_products(self):
        line_obj = self.env['product.sp.line']
        self.product_sp_line_ids = [(5, _, _)]
        if not self.partner_id:
            return
        query = '''select pp.id,ps.name,pu.name,pt.uom_id,pt.list_price,pp.product_mrp,ps.landing_cost,sq.qty from product_supplierinfo as ps
left join product_template as pt
on pt.id = ps.product_tmpl_id
left join product_product as pp
on pp.product_tmpl_id = pt.id
left join product_uom as pu
on pu.id = pt.uom_id
left join 
(select sum(qty) as qty,product_id from stock_quant
left join stock_location
on stock_quant.location_id = stock_location.id
where stock_location.usage = 'internal'
group by product_id) as sq
on sq.product_id = pp.id

where ps.name = %s and ps.product_tmpl_id not in
(
select ps.product_tmpl_id from product_supplierinfo as ps
    where ps.name <> %s
)
'''

        self.env.cr.execute(query, (self.partner_id.id,self.partner_id.id))
        for row in self.env.cr.dictfetchall():

            # margin = (row['product_mrp'] - row['landing_cost']) if (row['product_mrp'] - row['landing_cost']) > 0 else 0
            # list_price = (row['product_mrp'] - (((margin) * self.discount) / 100))

            values = {
                'product_id':row['id'],
                'uom_id':row['uom_id'],
                'on_hand':row['qty'],
                'landing_cost':row['landing_cost'] if row['landing_cost'] else 0,
                'mrp':row['product_mrp'] if row['product_mrp'] else 0,
                'sell_price':row['list_price']

            }

            order_line_var1 = line_obj.new(values)
            # line_obj += order_line_var1
            self.product_sp_line_ids += order_line_var1


    def change_product_price(self):
        for sp in self.product_sp_line_ids:
            sp.product_id.product_mrp=sp.mrp
            sp.product_id.lst_price = sp.sell_price

        return
class Product_SP_line(models.Model):
    _name = 'product.sp.line'

    product_id = fields.Many2one('product.product',string="Product",domain=[('can_be_sold','=',True)],readonly=True)
    uom_id = fields.Many2one('product.uom', 'Unit of Measure',readonly=True)
    on_hand = fields.Float('Onhand',default=0,readonly=True)
    landing_cost = fields.Float('Landing Cost',default=0,readonly=True)
    mrp = fields.Float('MRP',default=0)
    sell_price = fields.Float('Sell Price',default=0)
    product_sp_id = fields.Many2one('product.sp', string='Product Sp Reference',
                                       ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env['res.company']._company_default_get('product.sp.line'))


