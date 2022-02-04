# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportCategory(models.AbstractModel):

    _name = 'report.cog_report.cog_report_pdf'

    def get_lines(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        gp_filter = data['form']['gp_filter']

        sl = 0
        query = '''
            SELECT product_template.name as product,product_template.landing_cost as landingcost,sum(pos_order_line.qty) as qty,product_product.id as product_id,
            round(sum((pos_order_line.qty)  * ( pos_order_line.price_unit * (1 - (pos_order_line.discount) / 100.0))) * 100 / (100+COALESCE(account_tax.amount,'0')),2)  as taxable,
            round(sum((pos_order_line.qty * pos_order_line.price_unit) - pos_order_line.discount),2) as total  
 
            FROM 
                public.pos_order_line
                left join public.pos_order   on (pos_order.id = pos_order_line.order_id)
            left join public.product_product   on (pos_order_line.product_id = product_product.id)
                left join public.product_template   on (product_template.id = product_product.product_tmpl_id)
                left join public.product_taxes_rel on (product_taxes_rel.prod_id = product_template.id)
                left join public.account_tax on (product_taxes_rel.tax_id = account_tax.id)
 
 
                where
                pos_order.state in ('paid','done','invoiced')  
                AND to_char(date_trunc('day',pos_order.date_order),'YYYY-MM-DD')::date between %s and %s
                AND pos_order_line.company_id= %s
                group by 
                account_tax.amount,product_template.id,product_product.id
        '''
        self.env.cr.execute(query, ( date_start, date_end,company_id

                                        ))

        for row in self.env.cr.dictfetchall():
            cost = 0
            gross_profit = 0
            gross_profit_per = 0
            quantity = 0
            landingcost=0
            query1 = '''
                        SELECT pph.product_id as product_id ,pph.cost as cost,pph.id as id,pt.landing_cost as landingcost FROM 
                                                    product_price_history as pph 
                                                    left join product_product as pp on(pp.id=pph.product_id)
                                                    left join product_template as pt on(pt.id=pp.product_tmpl_id)
                                                    WHERE pph.product_id = %s
                                    and pph.company_id = %s ORDER BY pph.id DESC LIMIT 1
                                    '''
            # query1 = '''
            # SELECT product_id,cost,id FROM product_price_history  WHERE product_id = %s and company_id = %s ORDER BY id DESC LIMIT 1
            # '''
            self.env.cr.execute(query1, (row['product_id'], company_id

                                         ))
            for ans in self.env.cr.dictfetchall():
                cost = ans['cost'] if ans['cost'] else 0
                landingcost = ans['landingcost'] if ans['landingcost'] else 0
            if not cost:
                query2 = '''
                                select sum(mrp_bom_line.product_qty) as product_qty,mrp_bom_line.product_id
                                from mrp_bom_line 
                                left join mrp_bom on mrp_bom.id = mrp_bom_line.bom_id
                                left join product_template on product_template.id = mrp_bom.product_tmpl_id
                                left join product_product on product_product.product_tmpl_id = product_template.id
                                where product_product.id = %s and mrp_bom.company_id = %s
                                group by mrp_bom_line.product_id
                            '''
                self.env.cr.execute(query2, (row['product_id'], company_id

                                             ))
                for answer in self.env.cr.dictfetchall():
                    quantity = answer['product_qty'] if answer['product_qty'] else 0
                    query3 = ''' 
                                    SELECT pph.product_id as product_id ,pph.cost as cost,pph.id as id,pt.landing_cost as landingcost FROM 
                                                    product_price_history as pph 
                                                    left join product_product as pp on(pp.id=pph.product_id)
                                                    left join product_template as pt on(pt.id=pp.product_tmpl_id)
                                                    WHERE pph.product_id = %s
                                    and pph.company_id = %s ORDER BY pph.id DESC LIMIT 1
                                 '''
                    self.env.cr.execute(query3, (answer['product_id'], company_id

                                                 ))
                    for answer1 in self.env.cr.dictfetchall():
                        cost = answer1['cost'] if answer1['cost'] else 0
                        landingcost = answer1['landingcost'] if answer1['landingcost'] else 0



            sl = sl + 1
            purchase_cost = (cost*row['qty']*quantity) if quantity else (cost*row['qty'])
            # qty = quantity*row['qty'] if quantity else row['qty']
            # tot_qtyland = row['qty']*quantity*landingcost if quantity else (landingcost*row['qty'])

            gross_profit = row['taxable']-(purchase_cost) if row['taxable'] != 0 else 0
            gross_profit_per = round((gross_profit/row['taxable'])*100,2) if row['taxable'] != 0 else 0
            tot_land = row['landingcost']*row['qty'] if row['landingcost'] else 0


            if gp_filter:
                if gross_profit_per < gp_filter:

                    res = {
                        # 'tot_qtyland':tot_qtyland,
                        'landingcost': row['landingcost'] if row['landingcost'] else 0,
                        'tot_land': row['qty']*quantity*landingcost if quantity else (landingcost*row['qty']),
                        'sl_no': sl,
                        'product': row['product'],
                        'qty':row['qty'],
                        'sale':row['total'],
                        'cost': (cost*quantity) if quantity else (cost) ,
                        'gross_profit': gross_profit,
                        'gross_profit_per':gross_profit_per,
                        'gp_below': gross_profit_per if gross_profit_per < gp_filter else 0,
                        'gp_below_0':  0,
                        'gp_below_5': 0,
                        'gp_below_10':  0,


                    }
                    lines.append(res)
            else:
                res = {
                    # 'tot_qtyland': tot_qtyland,
                    'landingcost': row['landingcost'] if row['landingcost'] else 0,
                    'tot_land': row['qty']*quantity*landingcost if quantity else (landingcost*row['qty']),
                    'sl_no': sl,
                    'product': row['product'],
                    'qty': row['qty'],
                    'sale': row['total'],
                    'cost': (cost*quantity) if quantity else (cost),
                    'gross_profit': gross_profit,
                    'gross_profit_per': gross_profit_per,
                    'gp_below_0': gross_profit_per if gross_profit_per < 0 else 0,
                    'gp_below_5': gross_profit_per if 0 >= gross_profit_per and  gross_profit_per< 5 else 0,
                    'gp_below_10': gross_profit_per if 5 >= gross_profit_per and  gross_profit_per< 10 else 0,
                    'gp_below':  0,

                }

                lines.append(res)
        if lines:
            return lines
        else:
            return []


    @api.model
    def render_html(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        gp_filter = data['form']['gp_filter']

        valuesone = self.get_lines(data)
        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()


        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'date_end': date_object_date_end.strftime('%d-%m-%Y'),
            'valuesone': valuesone,
            'gp_filter':gp_filter,
        }

        return self.env['report'].render('cog_report.cog_report_pdf', docargs)
