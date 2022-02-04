# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Reportfastsale(models.AbstractModel):

    _name = 'report.qlty_fastsale_xls.fastsale_report_pdf'

    def get_lines(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        category_id = data['form']['category_id']
        if category_id:

            query = '''

                 select ROW_NUMBER() OVER(ORDER BY dd.id ASC) AS slno,
            dd.id as id,dd.pname as pname,dd.salepos_total as salepos_total ,
            dd.sale_total as sale_total,dd.pur_total as pur_total,dd.onhand as onhand,dd.valuation as valuation,
            dd.quantitypos as posquantity,dd.quantitysale as salequantity,dd.salecost as salecost
             from (
            (
    			  select sh.product_id as id ,pt.name as pname, sum (sh.quantity) as onhand
    			  ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
    			  from stock_history as sh
             left join product_product as pp on(pp.id=sh.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
              where  sh.company_id = %s
               and   pt.categ_id = %s group by sh.product_id,pt.name
                 ) a
                                            left join
            (
            select aal.product_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale
             from
            account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
    	 left join product_product as pp on(pp.id=aal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
            where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
            and  aa.company_id=%s and  pt.categ_id = %s
           group by aal.product_id
           ) b
                                          on a.id=b.product_id
                                          left join
            (
            select aaal.product_id ,sum(aaal.price_subtotal) as pur_total from
            account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
            where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
            and  aaa.company_id=%s  and    pt.categ_id =%s
    	group by aaal.product_id
    	) c
            on a.id=c.product_id
            				left join
            (
            select pol.product_id  ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
             from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
             left join product_product as pp on(pp.id=pol.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
             where
             po.state in  ('done', 'paid','invoiced')
            and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
             and pol.company_id=%s
             and  pt.categ_id =%s
             group by pol.product_id
                ) d
                                            on a.id=d.product_id
                                            left join

     (
      select pt.id as product_id ,sum (sh.quantity) as onhands,
                                            round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),0)) as salecost
    	 from stock_history as sh
             left join product_product as pp on(pp.id=sh.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
             left join product_category pc on (pc.id=pt.categ_id)
              where  available_in_pos =True
              and sh.quantity < 0
              and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between %s and %s and
              sh.company_id = %s
                group by pt.id

                ) f
                                            on a.id=f.product_id
            ) as dd


                                    '''

            self.env.cr.execute(query, (company_id, category_id,
                                        date_start, date_end, company_id, category_id,
                                        date_start, date_end, company_id, category_id,
                                        date_start, date_end, company_id, category_id,
                                        date_start, date_end, company_id
                                        ))

            for row in self.env.cr.dictfetchall():

                if row['salecost'] < 0:
                    row['salecost'] = (row['salecost'] if row['salecost'] else 0) * -1

                sale = 0
                possale = 0
                purtotal = 0
                sale = row['sale_total'] if row['sale_total'] else 0
                possale = row['salepos_total'] if row['salepos_total'] else 0
                purtotal = row['pur_total'] if row['pur_total'] else 0
                onhandtotal = row['valuation'] if row['valuation'] else 0
                totalsale = sale + possale
                totalsaleqty = row['salequantity'] if row['salequantity'] else 0
                totalposqty = row['posquantity'] if row['posquantity'] else 0
                totalsalecost = row['salecost'] if row['salecost'] else 0

                res = {
                    'sl_no': row['slno'],
                    'id': row['id'],
                    'pname': row['pname'] if row['pname'] else '',
                    'sale_total': round(totalsale, 0),
                    'pur_total': round(purtotal, 0),
                    'onhand': round(onhandtotal, 0),
                    'totalsalecost': round(totalsalecost, 0),
                    'profit': round((totalsale - totalsalecost), 0)
                }

                lines.append(res)
        else:

            query = '''



         select ROW_NUMBER() OVER(ORDER BY dd.id ASC) AS slno,
            dd.id as id,dd.pname as pname,
            dd.salepos_total as salepos_total ,
            dd.sale_total as sale_total,
            dd.pur_total as pur_total,
            dd.quantitypos as posquantity,
            dd.quantitysale as salequantity,
            dd.onhand as onhand,
            dd.valuation as valuation,
            dd.salecost as salecost

             from
            (
            (

    	select pt.categ_id as id ,pc.name as pname, sum (sh.quantity) as onhand,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
    	 from stock_history as sh
             left join product_product as pp on(pp.id=sh.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
             left join product_category pc on (pc.id=pt.categ_id)
              where  sh.company_id = %s and available_in_pos =True
                group by pt.categ_id,pc.name

                 ) a

                                            left join
            (
            select  pt.categ_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale from
            account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
    	 left join product_product as pp on(pp.id=aal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)

            where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
            and  aa.company_id= %s
           group by  pt.categ_id

           ) b

                                          on a.id=b.categ_id
                                          left join
            (

            select  pt.categ_id ,sum(aaal.price_subtotal) as pur_total from
            account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)


            where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
            and  aaa.company_id= %s
    	group by  pt.categ_id
    	) c
            on c.categ_id=a.id
            			left join
            (
            select  pt.categ_id  ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
             from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
             left join product_product as pp on(pp.id=pol.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
             where
             po.state in  ('done', 'paid','invoiced')
            and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
             and pol.company_id= %s
             group by  pt.categ_id
                ) d
                                            on a.id=d.categ_id
                                            left join
                                            (
                                            select pt.categ_id as categ_id ,sum (sh.quantity) as onhands,
                                            round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),0)) as salecost
    	 from stock_history as sh
             left join product_product as pp on(pp.id=sh.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
             left join product_category pc on (pc.id=pt.categ_id)
              where  available_in_pos =True
              and sh.quantity <0
              and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between %s and %s
              and sh.company_id = %s
                group by pt.categ_id

                                            ) f on a.id =f.categ_id
            ) as dd
                                                '''

            self.env.cr.execute(query, (company_id,
                                        date_start, date_end, company_id,
                                        date_start, date_end, company_id,
                                        date_start, date_end, company_id,
                                        date_start, date_end, company_id,
                                        ))

            for row in self.env.cr.dictfetchall():

                if row['salecost'] < 0:
                    row['salecost'] = (row['salecost'] if row['salecost'] else 0) * -1

                sale = 0
                possale = 0
                purtotal = 0
                sale = row['sale_total'] if row['sale_total'] else 0
                possale = row['salepos_total'] if row['salepos_total'] else 0
                purtotal = row['pur_total'] if row['pur_total'] else 0
                onhandtotal = row['valuation'] if row['valuation'] else 0
                totalsale = sale + possale
                totalsaleqty = row['salequantity'] if row['salequantity'] else 0
                totalposqty = row['posquantity'] if row['posquantity'] else 0
                totalsalecost = row['salecost'] if row['salecost'] else 0

                res = {
                    'sl_no': row['slno'],
                    'id': row['id'],
                    'pname': row['pname'] if row['pname'] else '',
                    'sale_total': round(totalsale, 0),
                    'pur_total': round(purtotal, 0),
                    'onhand': round(onhandtotal, 0),
                    'totalsalecost': round(totalsalecost, 0),
                    'profit': round(totalsale - totalsalecost, 0)
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
        category_id = data['form']['category_id']
        category_name = self.env["product.category"].browse(category_id).name
        valuesone = self.get_lines(data)
        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        if category_id:
            reportname = "Category Wise Report"
            productname = "Product"
        else:
            reportname = "All Category Report"
            productname = "Category"

        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'date_end': date_object_date_end.strftime('%d-%m-%Y'),
            'category_name': category_name  if category_name else 'All Category Report' ,
            'productname' :productname,
            'data': data['form'],
            'time': time,
            'valuesone': valuesone,
        }

        return self.env['report'].render('qlty_fastsale_xls.fastsale_report_pdf', docargs)
