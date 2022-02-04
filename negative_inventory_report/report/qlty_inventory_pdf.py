from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime

from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from odoo import models, fields, api,_
import time
import datetime
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta



class Qltyvendorwisepdfbrand(models.AbstractModel):
    _name ='report.negative_inventory_report.qlty_inventory_pdf'

    def get_lines(self, data):
        lines = []
        product = []
        average_cost = 0
        date_start = data['form']['date_start']

        company_id = data['form']['company_id']

        product = self.env["product.product"].search([])

        query1 = """select
               dd.id as id,dd.pname as pname,
               dd.catname as catname,
               dd.sale_date as sale_date,
               dd.pur_date as pur_date,
               dd.onhand as onhand,
              dd.mrp as mrp,dd.list_price as list_price,dd.costp as cost

                from (

    (select sh.product_id as id ,max(pt.name) as pname,
       			  pt.product_mrp as mrp ,pt.list_price as list_price,
       			  COALESCE(sum(sh.quantity),0)  as onhand ,
       			  max(pc.name) as catname

       			  from stock_history as sh
                left join product_product as pp on(pp.id=sh.product_id)
                left join product_template pt on (pt.id=pp.product_tmpl_id)
                left join product_category pc on (pc.id=sh.product_categ_id)

                where to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date <=%s

                 group by sh.product_id,pt.id having sum(sh.quantity)<0 order by pname 
                    ) a 






                                               left join
               (
               select aal.product_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale,
               max(aa.date_invoice) as sale_date
                from
               account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
       	 left join product_product as pp on(pp.id=aal.product_id)
                left join product_template pt on (pt.id=pp.product_tmpl_id)
               where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice <=%s
               and  aa.company_id= %s
              group by aal.product_id
              ) b
                                             on a.id=b.product_id
                                             left join
               (
               select aaal.product_id ,sum(aaal.price_subtotal) as pur_total,max(aaa.date_invoice) as pur_date from
               account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
       	left join product_product as pp on(pp.id=aaal.product_id)
                left join product_template pt on (pt.id=pp.product_tmpl_id)
               where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice <=%s
               and  aaa.company_id= %s
       	group by aaal.product_id
       	) c
               on a.id=c.product_id
               
               
               left join

            (

select aaal.product_id,
max(aaal.price_unit) as costp from 
	account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)

              where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid')
               and aaa.date_invoice <=%s and aaal.invoice_id in
             (select max(aaal.invoice_id) from 
account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
            where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice <=%s 
            and aaa.date_invoice in (select max(aaa.date_invoice) from account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
            where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') 
            and aaa.date_invoice <=%s group by  aaal.product_id) 
            group by aaal.product_id )group by aaal.product_id


            )d on a.id=d.product_id



               ) as dd order by dd.pname

       """

        self.env.cr.execute(query1, (date_start,
                                     date_start, company_id,
                                     date_start, company_id,date_start,date_start,date_start,

                                     ))

        for row in self.env.cr.dictfetchall():
            sale = 0
            possale = 0
            purtotal = 0
            pname = row['pname'] if row['pname'] else 0
            catname = row['catname'] if row['catname'] else 0
            sale_date = row['sale_date'] if row['sale_date'] else ""
            pur_date = row['pur_date'] if row['pur_date'] else ""
            # purchase_date = datetime.strptime(pur_date, '%Y-%m-%d').strftime('%d-%m-%Y')
            # sales_date = datetime.strptime(sale_date, '%Y-%m-%d').strftime('%d-%m-%Y')
            if pur_date != "":

                purchase_date = datetime.strptime(pur_date, '%Y-%m-%d').strftime('%d-%m-%Y')
            else:
                purchase_date = ""

            if sale_date != "":

                sales_date = datetime.strptime(sale_date, '%Y-%m-%d').strftime('%d-%m-%Y')
            else:
                sales_date = ""

            onhand = row['onhand'] if row['onhand'] else 0
            mrp = row['mrp'] if row['mrp'] else 0
            list_price = row['list_price'] if row['list_price'] else 0


            query2 = '''
                                   select aaal.product_id,
max(aaal.price_unit) as costpt from 
	account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)

              where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid')
               and aaa.date_invoice <=%s and aaal.product_id = %s and aaa.date_invoice in
             (select max(aaa.date_invoice) from 
account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
            where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice <=%s and aaal.product_id = %s 
            and aaal.invoice_id in (select max(aaal.invoice_id) from account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
            where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') 
            and aaa.date_invoice <=%s and aaal.product_id = %s group by  aaal.product_id) 
            group by aaal.product_id )group by aaal.product_id
                                                '''
            # query1 = '''
            # SELECT product_id,cost,id FROM product_price_history  WHERE product_id = %s and company_id = %s ORDER BY id DESC LIMIT 1
            # '''
            self.env.cr.execute(query2, (date_start,row['id'],date_start,row['id'],date_start,row['id']



                                         ))


            cost=0
            for ans in self.env.cr.dictfetchall():
                cost = ans['costpt'] if ans['costpt'] else 0

            res = {
                'id': row['id'] if row['id'] else '',
                'pname': row['pname'] if row['pname'] else '',
                'catname': row['catname'] if row['catname'] else '',
                'sale_date': sales_date,
                'pur_date': purchase_date,
                'onhand': row['onhand'] if row['onhand'] else 0,
                'mrp': row['mrp'] if row['mrp'] else 0,
                'list_price': row['list_price'] if row['list_price'] else 0,
                'cost': cost ,

            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []

    @api.model
    def render_html(self, docids, data=None, config_id=None):

        date_start = data['form']['date_start']
        company_id = data['form']['company_id']


        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        get_brand = self.get_lines(data)


        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'data': data['form'],
            'time': time,
            'valuesone': get_brand,
            # 'config': config,
            # 'configures': configures,
            'data': data['form'],
            'doc_ids': self.ids,
            'data': data['form'],
            'doc_ids': self.ids,

            # 'get_lines': get_lines if get_lines else 0,
            # 'get_brand': get_brand if get_brand else 0,

        }


        return self.env['report'].render('negative_inventory_report.qlty_inventory_pdf', docargs)