from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime

from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from odoo import models, fields, api,_
import time
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta



class Productmarginpdf(models.AbstractModel):
    _name ='report.product_margin_pdf.qlty_brand_pdf'

    def get_lines(self,data):

        lines = []
        product = []
        average_cost = 0
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']

        # query2 = """
        #
        #             select COALESCE(sum(CASE dd.amount WHEN dd.amount THEN dd.amount ELSE 0 END ),0)  as amount,
        #            COALESCE(sum(CASE dd.expense WHEN dd.expense THEN dd.expense ELSE 0 END ),0)  as expense
        #            from (
        #             select
        #                         round((case
        #                           when l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance >0
        #                          then  l.debit
        #                         else 0 end  ),2) as amount,
        #                         round((case
        #                          when l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance < 0 and payment_id is not null
        #                          then  l.credit
        #                        when l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance < 0
        #                         then  l.credit
        #
        #                         else 0 end  ),2) as expense  ,
        #                         m.state as state
        #                         from account_move_line l
        #                         full join account_account_type t on(t.id=l.user_type_id)
        #                         full join  account_move m on (m.id=l.move_id)
        #                         full join account_journal j on (j.id=m.journal_id)
        #                         left join account_account as ac on(ac.id=l.account_id)
        #
        #
        #                         where t.name='Expenses' and ac.name<>'Purchase Expense' and
        #            		    m.date BETWEEN %s and %s and m.company_id = %s and
        #
        #                              (  l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance >0
        #                        or
        #                        l.user_type_id=(select id from account_account_type where name='Expenses' ) and payment_id is not null
        #                        or
        #                        l.user_type_id=(select id from account_account_type where name='Expenses')
        #                        or
        #                        l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance < 0 )
        #                         )
        #
        #                        as dd
        #
        #             """

        query4="""
        
        
        
       select 
	sum(kk.amount) as amount,
	sum(kk.expense) as expense,
	--kk.month as month,
	ddd.month as month,
	sum(ddd.sale_qty) as sale_qty,
	sum(ddd.sale_amount)as sale_amount,
	sum(ddd.price_unit)as price_unit,
	sum(ddd.price_subtotal) as price_subtotal,
	sum(ddd.price_subtotal_taxinc) as price_subtotal_taxinc,
	sum(ddd.mrp) as mrp,
	sum(ddd.landing_cost) as landing_cost,
	sum(ddd.list_price) as list_price,
	
	
	sum(vv.cost) as cost59
	
	
	--,(ddd.id) as product_id








 from (select SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.quantity  ELSE ai.quantity END) as sale_qty,
 to_char(a.date_invoice,'YYYY/MM') as month,
                   SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END) as sale_amount,
                   sum(ai.price_unit) as price_unit,sum(ai.price_subtotal) as price_subtotal,sum(ai.price_subtotal_taxinc) as price_subtotal_taxinc,
                   sum(pt.product_mrp) as mrp,sum(pt.landing_cost) as landing_cost,sum(pt.list_price) as list_price,max(pt.name) as name,max(p.id) as id
                   from account_invoice_line as ai
                       left join account_invoice as a
                       on a.id=ai.invoice_id
                       left join product_product as p
                       on ai.product_id =p.id
                       left join product_template as pt
                       on pt.id = p.product_tmpl_id
                       

                       

                       where a.type in ('out_invoice','out_refund') and a.state in ('open','paid')
                       and a.company_id = %s and a.date_invoice BETWEEN %s and %s 
                       group by to_char(a.date_invoice,'YYYY/MM')) ddd

                       left join
                       
                       
                       (select SUM(CASE WHEN yy.product_qty <0  then (yy.product_qty)  ELSE 0 END) as qty,
                      max(yy.product_id) as product_id,
                     SUM(CASE WHEN (yy.cost) <0 then (yy.cost) ELSE 0 END) as cost,

                     


                    
                     (yy.month) as month from (select 

                      *



                      from  (   select sum(mbl.product_qty) as product_qty,max(p.id) as product_id,

sum((pph.cost)*(mbl.product_qty)*(ai.quantity)) as cost,

to_char(a.date_invoice,'YYYY/MM') as month


  from account_invoice_line as ai
                       left join account_invoice as a
                       on a.id=ai.invoice_id
                       left join product_product as p
                       on ai.product_id =p.id
                       left join product_template as pt
                       on p.product_tmpl_id =pt.id
                       left join mrp_bom as mr
                       on mr.product_tmpl_id=pt.id
                       left join mrp_bom_line as mbl
                       on mr.id = mbl.bom_id
                       left join product_price_history as pph
                       on pph.product_id=mbl.product_id

                        where a.type in ('out_invoice','out_refund') and a.state in ('open','paid')
                       and a.company_id = %s and a.date_invoice BETWEEN %s and %s
                       group by to_char(a.date_invoice,'YYYY/MM')
            ) pp 
                                
                                union all
                                
                                
                                    ( select sum(sh.quantity) as product_qty,
                                    max(pp.id) as product_id,
					
                                        round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as cost,
                                        to_char(sh.date,'YYYY/MM') as month
	 from stock_history as sh
         left join product_product as pp on(pp.id=sh.product_id)
         left join product_template pt on (pt.id=pp.product_tmpl_id)
         left join stock_move as sm on(sh.move_id=sm.id)
         left join stock_picking_type as spt on (spt.id=sm.picking_type_id)
         
          where  available_in_pos =True and spt.code <> 'internal'
          and sh.quantity <0
          and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between %s and %s
          and sh.company_id =%s
            group by  to_char(sh.date,'YYYY/MM')) )yy group by yy.month) as vv on vv.product_id=ddd.id
                                            
                                            left join
                                
                                
                                
                                

                       (select sum(case when(expense)<0 then -1*(expense) else 0 END) as expense,
                                COALESCE(sum(CASE ss.amount WHEN ss.amount THEN ss.amount ELSE 0 END ),0)  as amount,
                               ss.month as month
                              
                               
                               from (select max(ac.name),sum(l.credit-l.debit) as expense,sum(credit) as amount,
                               (to_char(m.date,'YYYY/MM') )as month
                                from account_move_line l
				full join account_move m on (m.id=l.move_id)
				full join account_account as ac on(ac.id=l.account_id)
                                full join account_account_type t on(t.id=ac.user_type_id)
                                
                                full join account_journal j on (j.id=m.journal_id)
                                
                                full join product_product as pp on(pp.id=l.product_id)

                                where t.name='Expenses'
                                and
                   		    m.date BETWEEN %s and %s and m.company_id = %s
                   		     group by month)ss group by ss.month )as kk on ddd.month=kk.month group by ddd.month order by ddd.month
                       
                       

         
        
        """

        self.env.cr.execute(query4, (
            company_id, date_start, date_end,
            company_id, date_start, date_end,
            date_start, date_end,company_id,
            date_start, date_end, company_id

                                     ))
        for row in self.env.cr.dictfetchall():
            expense = row['expense'] if row['expense'] else 0
            amount = row['amount'] if row['amount'] else 0
            cost = 0

            quantity = 0
            landingcost = 0
            sale = 0
            possale = 0
            purtotal = 0
            # bom_qty = row['bom_qty'] if row['bom_qty'] else 0
            sale_qty = row['sale_qty'] if row['sale_qty'] else 0
            sale_amount = row['sale_amount'] if row['sale_amount'] else 0
            price_unit = row['price_unit'] if row['price_unit'] else 0
            price_subtotal = row['price_subtotal'] if row['price_subtotal'] else 0
            price_subtotal_taxinc = row['price_subtotal_taxinc'] if row['price_subtotal_taxinc'] else 0
            mrp = row['mrp'] if row['mrp'] else 0
            landing_cost = row['landing_cost'] if row['landing_cost'] else 0
            list_price = row['list_price'] if row['list_price'] else 0
            # cost4 = row['costm'] if row['costm'] else 0
            cost5 = -1*row['cost59'] if row['cost59'] else 0
            month=row['month'] if row['month'] else 0
            cost = ((cost5)) if cost5 else 0
            print 'cost',cost
            margin =  ((price_subtotal-cost)-(expense))


            res = {

                        'expense':expense,
                        'amount':amount,

                        'sale_qty': sale_qty,
                        'sale_amount': sale_amount,
                        'price_unit': price_unit,
                        'price_subtotal': price_subtotal,
                        'price_subtotal_taxinc': price_subtotal_taxinc,
                        'mrp': mrp,
                        'landing_cost': landingcost,
                        'list_price': list_price,
                        'cost': cost,
                        'margin': margin if margin else 0,
                        'month':month,
                        'marginp': ((mrp - landingcost) / mrp) * 100 if mrp else 0,
                        'gross_margin':price_subtotal-cost,
                        'gross_percentage':((price_subtotal-cost)/price_subtotal)*100 if price_subtotal else 0,
                        'net_percentage':(((price_subtotal-cost)-expense)/price_subtotal)*100 if price_subtotal else 0

                    }
            lines.append(res)

        if lines:
            return lines
        else:
            return []






    # def get_lines(self, data):
    #     lines = []
    #     product = []
    #     average_cost = 0
    #     date_start = data['form']['date_start']
    #     date_end = data['form']['date_end']
    #     company_id = data['form']['company_id']
    #
    #     query = """
    #
    #
    #           select SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.quantity  ELSE ai.quantity END) as sale_qty,
    #                SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END) as sale_amount,
    #                sum(ai.price_unit) as price_unit,sum(ai.price_subtotal) as price_subtotal,sum(ai.price_subtotal_taxinc) as price_subtotal_taxinc,
    #                sum(pt.product_mrp) as mrp,sum(pt.landing_cost) as landing_cost,sum(pt.list_price) as list_price,sum(pph.cost) as cost,max(pt.name) as name
    #                from account_invoice_line as ai
    #                    left join account_invoice as a
    #                    on a.id=ai.invoice_id
    #                    left join product_product as p
    #                    on ai.product_id =p.id
    #                    left join product_template as pt
    #                    on pt.id = p.product_tmpl_id
    #
    #                    left join product_price_history as pph
    #                    on pph.product_id=p.id
    #
    #                    where a.type in ('out_invoice','out_refund') and a.state in ('open','paid')
    #                    and a.company_id = %s and a.date_invoice BETWEEN %s and %s
    #
    #            """
    #
    #     # query ="""
    #     #
    #     #
    #     select SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.quantity  ELSE ai.quantity END) as sale_qty,
    #         SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END) as sale_amount,
    #         max(ai.price_unit) as price_unit,sum(ai.price_subtotal) as price_subtotal,sum(ai.price_subtotal_taxinc) as price_subtotal_taxinc,
    #         max(pt.product_mrp) as mrp,max(pt.landing_cost) as landing_cost,max(pt.list_price) as list_price,max(pph.cost) as cost,max(pt.name) as name,
    #         ai.product_id from account_invoice_line as ai
    #             left join account_invoice as a
    #             on a.id=ai.invoice_id
    #             left join product_product as p
    #             on ai.product_id =p.id
    #             left join product_template as pt
    #             on pt.id = p.product_tmpl_id
    #
    #             left join product_price_history as pph
    #             on pph.product_id=p.id
    #
    #             where a.type in ('out_invoice','out_refund') and a.state in ('open','paid')
    #             and a.company_id = %s and a.date_invoice BETWEEN %s and %s
    #             GROUP BY ai.product_id
    #     #
    #     # """
    #     # query="""
    #     #
    #     #
    #     #
    #     #  select SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.quantity  ELSE ai.quantity END) as sale_qty,
    #     #                  SUM(CASE WHEN a.type = 'out_refund' and aat.name='Expenses' and ac.name <>'Purchase expense' then -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END) as expence,
    #     #     SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END) as sale_amount,
    #     #     max(ai.price_unit) as price_unit,sum(ai.price_subtotal) as price_subtotal,sum(ai.price_subtotal_taxinc) as price_subtotal_taxinc,
    #     #     max(pt.product_mrp) as mrp,max(pt.landing_cost) as landing_cost,max(pt.list_price) as list_price,max(pph.cost) as cost,max(pt.name) as name,
    #     #     ai.product_id from account_invoice_line as ai
    #     #         left join account_invoice as a
    #     #         on a.id=ai.invoice_id
    #     #         left join product_product as p
    #     #         on ai.product_id =p.id
    #     #         left join product_template as pt
    #     #         on pt.id = p.product_tmpl_id
    #     #         left join product_price_history as pph
    #     #         on pph.product_id=p.id
    #     #         left join account_account as ac
    #     #         on (ac.id=a.account_id)
    #     #         left join account_account_type as aat
    #     #         on aat.id=ac.user_type_id
    #     #
    #     #         where a.type in ('out_invoice','out_refund') and a.state in ('open','paid')
    #     #         and a.company_id = %s and a.date_invoice BETWEEN %s and %s
    #     #         GROUP BY ai.product_id
    #     #
    #     #
    #     #
    #     #
    #     #
    #     # """
    #     self.env.cr.execute(query, (company_id,
    #                                     date_start, date_end
    #                                     ))
    #     for row in self.env.cr.dictfetchall():
    #         sale = 0
    #         possale = 0
    #         purtotal = 0
    #         sale_qty = row['sale_qty'] if row['sale_qty'] else 0
    #         sale_amount = row['sale_amount'] if row['sale_amount'] else 0
    #         price_unit = row['price_unit'] if row['price_unit'] else 0
    #         price_subtotal = row['price_subtotal'] if row['price_subtotal'] else 0
    #         price_subtotal_taxinc = row['price_subtotal_taxinc'] if row['price_subtotal_taxinc'] else 0
    #         mrp = row['mrp'] if row['mrp'] else 0
    #         landing_cost = row['landing_cost'] if row['landing_cost'] else 0
    #         list_price = row['list_price'] if row['list_price'] else 0
    #         cost = row['cost'] if row['cost'] else 0
    #         name = row['name'] if row['name'] else 0
    #         # expence =row['expence'] if row['expence'] else 0
    #
    #         res = {
    #
    #
    #             'sale_qty':sale_qty,
    #             'sale_amount':sale_amount,
    #             'price_unit':price_unit,
    #             'price_subtotal':price_subtotal,
    #             'price_subtotal_taxinc':price_subtotal_taxinc,
    #             'mrp':mrp,
    #             'landing_cost':landing_cost,
    #             'list_price':list_price,
    #             'cost':cost,
    #             'name':name,
    #             'margin':mrp-landing_cost,
    #             'marginp':((mrp-landing_cost)/mrp)*100 if mrp else 0,
    #             # 'expence':expence
    #
    #         }
    #
    #         lines.append(res)
    #
    #     if lines:
    #         return lines
    #     else:
    #         return []

    @api.model
    def render_html(self, docids, data=None, config_id=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        get_lines = self.get_lines(data)
        # get_expence=self.get_expence(data)


        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'date_end': date_object_date_end.strftime('%d-%m-%Y'),
            'data': data['form'],
            'time': time,
            'valuesone': get_lines,
            # 'config': config,
            # 'configures': configures,
            'data': data['form'],
            'doc_ids': self.ids,
            'data': data['form'],
            'doc_ids': self.ids,
            # 'get_expence':get_expence


        }


        return self.env['report'].render('product_margin_pdf.qlty_brand_pdf', docargs)