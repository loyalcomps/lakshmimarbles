
import datetime
from datetime import datetime
from odoo.tools.translate import _
from odoo import models, fields, api


class CostChangedProductPdf(models.AbstractModel):
    _name ='report.retail_price_update.cost_change_product_report'

    def price_change(self,data):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']
        category = data['form']['category']
        lines =[]
        if category:
            query ='''select pol.product_id,pol.price_unit,pol.old_cost,sm.product_uom_qty,pt.name,pp.barcode,pc.name as category from stock_move as sm
                left join stock_picking as sp on sm.picking_id=sp.id
                left join purchase_order_line as pol on pol.id=sm.purchase_line_id
                left join product_product as pp on pp.id = pol.product_id
                left join product_template as pt on pt.id=pp.product_tmpl_id
                left join product_category as pc on pc.id = pt.categ_id
                where sp.state='done' and sm.purchase_line_id is not null and pol.price_unit != pol.old_cost and sm.company_id =%s
                and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date between %s and %s
                and pt.categ_id in %s order by pt.name 
            '''
            self.env.cr.execute(query, (company_id, start_date,end_date,tuple(category)))
            for row in self.env.cr.dictfetchall():
                onhand = self.env['product.product'].browse(row['product_id']).qty_available

                res = {
                    'article':row['product_id'],
                    'barcode': row['barcode'] if row['barcode'] else ' ',
                    'product': row['name'],
                    'new_cost': round(row['price_unit'],2) if row['price_unit'] else 0,
                    'old_cost': round(row['old_cost'],2) if row['old_cost'] else 0,
                    'category': row['category'],
                    'onhand': onhand if onhand else 0,
                    'received_qty': round(row['product_uom_qty'],2) if row['product_uom_qty'] else 0,
                }

                lines.append(res)
        else:

            query='''select pol.product_id,pol.price_unit,pol.old_cost,sm.product_uom_qty,pt.name,pp.barcode from stock_move as sm
                left join stock_picking as sp on sm.picking_id=sp.id
                left join purchase_order_line as pol on pol.id=sm.purchase_line_id
                left join product_product as pp on pp.id = pol.product_id
                left join product_template as pt on pt.id=pp.product_tmpl_id
                where sp.state='done' and sm.purchase_line_id is not null and pol.price_unit != pol.old_cost and sm.company_id =%s
                and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date between %s and %s order by pt.name'''

            self.env.cr.execute(query, (company_id, start_date, end_date,))
            for row in self.env.cr.dictfetchall():
                onhand = self.env['product.product'].browse(row['product_id']).qty_available

                res = {
                    'article': row['product_id'],
                    'barcode': row['barcode'] if row['barcode'] else ' ',
                    'product': row['name'],
                    'new_cost': round(row['price_unit'], 2) if row['price_unit'] else 0,
                    'old_cost': round(row['old_cost'], 2) if row['old_cost'] else 0,
                    'onhand': onhand if onhand else 0,
                    'received_qty': round(row['product_uom_qty'], 2) if row['product_uom_qty'] else 0,
                }

                lines.append(res)


        if lines:
            return lines
        else:
            return []

    @api.model
    def render_html(self, docids, data=None, config_id=None):

        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']
        category = data['form']['category']
        price_change_date = self.price_change(data)

        date_object_startdate = datetime.strptime(start_date, '%Y-%m-%d').date()
        date_object_enddate = datetime.strptime(end_date, '%Y-%m-%d').date()


        docargs = {
            'doc_ids': self.ids,
            'start_date': date_object_startdate.strftime('%d-%m-%Y'),
            'end_date': date_object_enddate.strftime('%d-%m-%Y'),
            'product_data':price_change_date,
            'category':category,


        }

        return self.env['report'].render('retail_price_update.cost_change_product_report', docargs)