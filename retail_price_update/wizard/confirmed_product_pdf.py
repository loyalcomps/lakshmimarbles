
import datetime
from datetime import datetime
from odoo.tools.translate import _
from odoo import models, fields, api


class CostChangedProductPdf(models.AbstractModel):
    _name ='report.retail_price_update.confirmed_product_report'

    def price_change(self,data):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']
        category = data['form']['category']
        lines =[]
        if category:
            query ='''select cwl.product_id,cwl.current_price,cwl.new_price,cwl.mrp,cwl.on_hand,pt.name,pc.name as category from confirm_window_line as cwl
                
                left join product_product as pp on pp.id = cwl.product_id
                left join product_template as pt on pt.id=pp.product_tmpl_id
                left join product_category as pc on pc.id = pt.categ_id
                where cwl.confirm=true and cwl.company_id =%s
                and to_char(date_trunc('day',cwl.date),'YYYY-MM-DD')::date between %s and %s
                and pt.categ_id in %s order by pt.name
            '''
            self.env.cr.execute(query, (company_id, start_date,end_date,tuple(category)))
            for row in self.env.cr.dictfetchall():

                res = {
                    'product': row['name'],
                    'current_price': round(row['current_price'],2) if row['current_price'] else 0,
                    'new_price': round(row['new_price'],2) if row['new_price'] else 0,
                    'category': row['category'],
                    'onhand': round(row['on_hand'],2) if row['on_hand'] else 0,
                    'mrp': round(row['mrp'],2) if row['mrp'] else 0,
                }

                lines.append(res)
        else:

            query='''select cwl.product_id,cwl.current_price,cwl.new_price,cwl.mrp,cwl.on_hand,
                pt.name from confirm_window_line as cwl
                
                left join product_product as pp on pp.id = cwl.product_id
                left join product_template as pt on pt.id=pp.product_tmpl_id
                
                where cwl.confirm=true and cwl.company_id =%s
                and to_char(date_trunc('day',cwl.date),'YYYY-MM-DD')::date between %s and %s
                order by pt.name'''

            self.env.cr.execute(query, (company_id, start_date, end_date,))
            for row in self.env.cr.dictfetchall():
                onhand = self.env['product.product'].browse(row['product_id']).qty_available

                res = {
                    'product': row['name'],
                    'current_price': round(row['current_price'],2) if row['current_price'] else 0,
                    'new_price': round(row['new_price'],2) if row['new_price'] else 0,

                    'onhand': round(row['on_hand'],2) if row['on_hand'] else 0,
                    'mrp': round(row['mrp'],2) if row['mrp'] else 0,
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

        return self.env['report'].render('retail_price_update.confirmed_product_report', docargs)