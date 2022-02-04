from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime


class Brandrwise(ReportXlsx):


    def get_expence(self,data):

        lines = []
        product = []
        average_cost = 0
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']

        query2 = """
        
        
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
	sum(vv.cost) as cost,
	sum(pp.product_qty) as bom_qty,
	sum(pp.costm) as costm
	--,(ddd.id) as product_id








 from (select SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.quantity  ELSE ai.quantity END) as sale_qty,
 max(case to_char(a.date_invoice,'mm') 
 when '01' then 'January' when '02' then 'February'  
 when '03' then 'March' when '04' then 'April'
 when '05' then 'May' when '06' then 'June'
 when '07' then 'July' when '08' then 'August'
  when '09' then 'September' when '10' then 'October' when '11' then 'November' when '12' then 'december'end) as month,
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
                       group by to_char(a.date_invoice,'month'),p.id) ddd

                       left join
                       
                       
                        (
                                            select sh.product_id as product_id ,sum (sh.price_unit_on_quant) as cost1,
                                            sum (pph.cost) as cost,
                                            max(case to_char(sh.date,'mm') 
 when '01' then 'January' when '02' then 'February'  
 when '03' then 'March' when '04' then 'April'
 when '05' then 'May' when '06' then 'June'
 when '07' then 'July' when '08' then 'August'
  when '09' then 'September' when '10' then 'October' when '11' then 'November' when '12' then 'december'end) as month
                                           
    	 from stock_history as sh
             left join product_product as pp on(pp.id=sh.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
             left join product_category pc on (pc.id=pt.categ_id)
             left join product_price_history as pph on(pph.product_id =pp.id)
              where  
              
              to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between %s and %s 
              and sh.company_id = %s
                       group by to_char(sh.date,'month'),sh.product_id
              
                

                                            ) as vv on vv.product_id=ddd.id
                                            
                                            left join
                                            
                                            
                                             (select sum(mrp_bom_line.product_qty) as product_qty,
                        sum (sh.price_unit_on_quant) as costm,
                        mrp_bom_line.product_id as product_id,
                        max(case to_char(sh.date,'mm') 
 when '01' then 'January' when '02' then 'February'  
 when '03' then 'March' when '04' then 'April'
 when '05' then 'May' when '06' then 'June'
 when '07' then 'July' when '08' then 'August'
  when '09' then 'September' when '10' then 'October' when '11' then 'November' when '12' then 'december'end) as month
                                from mrp_bom_line 
                                left join mrp_bom on mrp_bom.id = mrp_bom_line.bom_id
                                left join product_template on product_template.id = mrp_bom.product_tmpl_id
                                left join product_product on product_product.product_tmpl_id = product_template.id
                                left join stock_history as sh on(sh.product_id=product_product.id)
                                where mrp_bom.company_id = %s and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between %s and %s  
                                group by mrp_bom_line.product_id,to_char(sh.date,'month'))pp on pp.product_id=ddd.id
                                
                                left join

                       (select COALESCE(sum(CASE dd.amount WHEN dd.amount THEN dd.amount ELSE 0 END ),0)  as amount,
                   COALESCE(sum(CASE dd.expense WHEN dd.expense THEN dd.expense ELSE 0 END ),0)  as expense,
                   max(dd.month) as month,max(dd.id )as id
                   
                   from (
                    select 
                                round((case
                                  when l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance >0
                                 then  l.debit
                                else 0 end  ),2) as amount,
                                round((case
                                 when l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance < 0 and payment_id is not null
                                 then  l.credit
                               when l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance < 0
                                then  l.credit

                                else 0 end  ),2) as expense  ,
                                max(case to_char(m.date,'mm') 
 when '01' then 'January' when '02' then 'February'  
 when '03' then 'March' when '04' then 'April'
 when '05' then 'May' when '06' then 'June'
 when '07' then 'July' when '08' then 'August'
  when '09' then 'September' when '10' then 'October' when '11' then 'November' when '12' then 'december'end) as month,
                                l.user_type_id as user_type_id,pp.id as id
                                from account_move_line l
                                full join account_account_type t on(t.id=l.user_type_id)
                                full join  account_move m on (m.id=l.move_id)
                                full join account_journal j on (j.id=m.journal_id)
                                left join account_account as ac on(ac.id=l.account_id)
                                left join product_product as pp on(pp.id=l.product_id)


                                where t.name='Expenses' and ac.name<>'Purchase Expense' and
                   		    m.date BETWEEN %s and %s and m.company_id = %s and	    

                                     (  l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance >0
                               or
                               l.user_type_id=(select id from account_account_type where name='Expenses' ) and payment_id is not null
                               or
                               l.user_type_id=(select id from account_account_type where name='Expenses')
                               or
                               l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance < 0 )
                               group by l.user_type_id,l.balance,l.debit,l.credit,l.payment_id,pp.id  ) 
                               as dd)as kk on ddd.id=kk.id group by ddd.month order by ddd.month


                    select COALESCE(sum(CASE dd.amount WHEN dd.amount THEN dd.amount ELSE 0 END ),0)  as amount,
                   COALESCE(sum(CASE dd.expense WHEN dd.expense THEN dd.expense ELSE 0 END ),0)  as expense
                   from (
                    select 
                                round((case
                                  when l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance >0
                                 then  l.debit
                                else 0 end  ),2) as amount,
                                round((case
                                 when l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance < 0 and payment_id is not null
                                 then  l.credit
                               when l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance < 0
                                then  l.credit

                                else 0 end  ),2) as expense  ,
                                m.state as state
                                from account_move_line l
                                full join account_account_type t on(t.id=l.user_type_id)
                                full join  account_move m on (m.id=l.move_id)
                                full join account_journal j on (j.id=m.journal_id)
                                left join account_account as ac on(ac.id=l.account_id)


                                where t.name='Expenses' and ac.name<>'Purchase Expense' and
                   		    m.date BETWEEN %s and %s and m.company_id = %s and	    

                                     (  l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance >0
                               or
                               l.user_type_id=(select id from account_account_type where name='Expenses' ) and payment_id is not null
                               or
                               l.user_type_id=(select id from account_account_type where name='Expenses')
                               or
                               l.user_type_id= (select id from account_account_type where name='Expenses') and l.balance < 0 )
                                )

                               as dd 

                    """

        self.env.cr.execute(query2, (date_start, date_end, company_id

                                     ))
        for answer1 in self.env.cr.dictfetchall():
            expense = answer1['expense'] if answer1['expense'] else 0
            amount = answer1['amount'] if answer1['amount'] else 0

            res = {

                'expense':expense,
                'amount':amount

            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []


    def get_lines(self, data):
        lines = []
        product = []
        average_cost = 0
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        brand_id = data['form']['brand_id']
        brand_only = data['form']['brand_only']

        if brand_id:
            query1="""select ROW_NUMBER() OVER(ORDER BY dd.id ASC) AS slno,
                                           dd.id as id,dd.salepos_total as salepos_total ,dd.sale_total as sale_total,dd.purtotal as purtotal,
                                            dd.apsale_total as apsale_total,
                                            dd.apquantitysale as apsalequantity,
                                            (dd.sale_total-apsale_total) as invoice_saletotal,
                                            (dd.quantitysale-dd.apquantitysale) as invoice_quantitytotal,
                                            
                                            ((dd.sale_total-apsale_total)+dd.salepos_total) as ssale,
                                            

                                             dd.quantitypos as posquantity,
                                             dd.quantitysale as salequantity,
                                             dd.qtypur as qtypur,
                                              dd.freequantitypur as freequantitypur,
                                               (dd.qtypur+dd.freequantitypur) as quantitypur,
                                             dd.name as dname,
                                             dd.productname as pname,
                                             dd.pcname as pcname,
                                             dd.cscst as cscst


                                            from
                                            (

                                            (


                                            select max(sh.product_id) as id,max(pb.name) as name,max(pb.id) as pb,max(pt.name) as productname
                                          ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation,
                                          round(COALESCE(SUM(sm.price_unit * sm.product_qty),0)) as ion,max(pc.name) as pcname,max(pc.id)


                                         from stock_history  as sh
                                             left join product_product as pp on(pp.id=sh.product_id)
                                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                                         left join product_brand as pb on (pb.id=pp.brand_id) 
                                         left join product_category as pc on (pt.categ_id =pc.id)
                                         left join stock_move as sm on(sm.product_id = pp.id)


                                        where  sh.company_id=%s and pc.id = %s group by 
                                                                pb.id


                                                         ) a

                                                  left join      
                                    (
                                    select po.invoice_id,aal.product_id ,sum(aal.price_subtotal_taxinc) as apsale_total,sum(quantity) as apquantitysale,
                                    round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as apcccst

                                      from
                                    account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                                    left join pos_order as po on(po.invoice_id=aal.invoice_id)
                                    where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                                    and  aa.company_id= %s 
                                    and (aal.invoice_id=po.invoice_id)
                                    

                                    group by aal.product_id,po.invoice_id
                                                        ) b

                                                      on a.id=b.product_id

                                                      left join



                                                      (
                                    select aal.product_id ,sum(aal.price_subtotal_taxinc) as sale_total,sum(quantity) as quantitysale,
                                    round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as cccst

                                      from
                                    account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                                    
                                    where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                                    and  aa.company_id= %s 
                                    
                                    

                                    group by aal.product_id
                                                        ) h

                                                      on a.id=h.product_id

                                                      left join
                                    (

                                    select aaal.product_id ,sum(aaal.price_subtotal_taxinc) as purtotal,sum(quantity) as qtypur ,sum(free_qty) as freequantitypur,
                                    round(SUM(aaal.price_subtotal_taxinc/ nullif (aaal.quantity,0)),2) as cscst 
                        from
                                    account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                                    where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
                                    and  aaa.company_id= %s
                                      group by aaal.product_id) c

                                    on c.product_id=a.id

                                                left join

                    (
                                    select pp.brand_id,max(pb.name),pol.product_id ,(sum(round(((pol.qty * pol.price_unit) - pol.discount),2))) as salepos_total,(sum(pol.qty)) as quantitypos
                                     from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                     left join product_product as pp on(pp.id=pol.product_id)
                                    left join product_template pt on (pt.id=pp.product_tmpl_id)
                                    left join product_brand as pb on (pb.id=pp.brand_id) 

                                     where
                                     po.state in  ('done', 'paid','invoiced')
                                    and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and %s
                                    and pol.company_id= %s
                                    group by pol.product_id,pp.brand_id)f on a.id=f.product_id)dd order by ssale
"""
            query = '''

                                select ROW_NUMBER() OVER(ORDER BY dd.id ASC) AS slno,
                                               dd.id as id,dd.salepos_total as salepos_total ,dd.sale_total as sale_total,dd.purtotal as purtotal,

                                                dd.quantitypos as posquantity,
                                                dd.quantitysale as salequantity,
                                                dd.quantitypur as quantitypur,
                                                dd.name as dname,
                                                dd.productname as pname

                                               from
                                               (

                                               (



                                select sh.product_id as id,max(pb.name) as name,pb.id as pb,max(pt.name) as productname
                                             ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation,
                                             round(COALESCE(SUM(sm.price_unit * sm.product_qty),0)) as ion


                                            from stock_history  as sh
                                                left join product_product as pp on(pp.id=sh.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)
                                            left join product_brand as pb on (pb.id=pp.brand_id) 
                                            left join stock_move as sm on(sm.product_id = pp.id)


                                           where  sh.company_id=%s and pb.id in %s group by 
                                                                   sh.product_id,pb.id

                                                                    ) a

                                                                   left join

                                               (
                                               select aal.product_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale,
                                               round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as cccst

                                                 from
                                               account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                                               where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                                               and  aa.company_id= %s group by aal.product_id

                                                                   ) b

                                                                 on a.id=b.product_id

                                                                 left join
                                               (

                                               select aaal.product_id ,sum(aaal.price_subtotal) as purtotal,sum(quantity) as quantitypur ,
                                               round(SUM(aaal.price_subtotal_taxinc/ nullif (aaal.quantity,0)),2) as cscst 
                               	from
                                               account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                                               where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
                                               and  aaa.company_id= %s
                                                 group by aaal.product_id) c

                                               on c.product_id=a.id

                                                           left join

                               (
                                               select pp.brand_id,max(pb.name),pol.product_id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                                from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                                left join product_product as pp on(pp.id=pol.product_id)
                                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                                               left join product_brand as pb on (pb.id=pp.brand_id) 

                                                where
                                                po.state in  ('done', 'paid','invoiced')
                                               and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and %s
                                               and pol.company_id= %s
                                               group by pol.product_id,pp.brand_id)f on a.id=f.product_id)dd 

                                                                      '''
            self.env.cr.execute(query, (company_id, tuple(brand_id),
                                        date_start, date_end, company_id, date_start, date_end, company_id,
                                        date_start, date_end, company_id,
                                        ))

            for row in self.env.cr.dictfetchall():
                sale = 0
                possale = 0
                purtotal = 0
                sale = row['sale_total'] if row['sale_total'] else 0
                possale = row['salepos_total'] if row['salepos_total'] else 0
                purtotal = row['purtotal'] if row['purtotal'] else 0
                totalsale = sale + possale
                totalsaleqty = row['salequantity'] if row['salequantity'] else 0
                totalposqty = row['posquantity'] if row['posquantity'] else 0
                quantitypur = row['quantitypur'] if row['quantitypur'] else 0

                res = {
                    'sl_no': row['slno'],
                    'id': row['id'],
                    'pname': row['pname'] if row['pname'] else '',
                    'bname': row['dname'] if row['dname'] else '',
                    'sale': sale,
                    'possale': possale,
                    'purtotal': purtotal,
                    'totalsale': totalsale,
                    'totalsaleqty': totalsaleqty,
                    'totalposqty ': totalposqty,
                    'sqty': totalsaleqty + totalposqty,
                    'quantitypur': quantitypur
                }

                lines.append(res)

            if lines:
                return lines
            else:
                return []

    def get_brand(self, data):

        lines = []
        product = []
        average_cost = 0
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        brand_id = data['form']['brand_id']
        brand_only = data['form']['brand_only']

        query = '''

           select ROW_NUMBER() OVER(ORDER BY dd.id ASC) AS slno,
                                       dd.id as id,dd.salepos_total as salepos_total ,dd.sale_total as sale_total,dd.purtotal as purtotal,

                                        dd.quantitypos as posquantity,
                                        dd.quantitysale as salequantity,
                                        dd.quantitypur as quantitypur,
                                        dd.name as dname,
                                        dd.productname as pname

                                       from
                                       (

                                       (



                        select sh.product_id as id,max(pb.name) as name,pb.id as pb,max(pt.name) as productname
                                     ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation,
                                     round(COALESCE(SUM(sm.price_unit * sm.product_qty),0)) as ion


                                    from stock_history  as sh
                                        left join product_product as pp on(pp.id=sh.product_id)
                                    left join product_template pt on (pt.id=pp.product_tmpl_id)
                                    left join product_brand as pb on (pb.id=pp.brand_id) 
                                    left join stock_move as sm on(sm.product_id = pp.id)


                                   where  sh.company_id=%s group by 
                                                           sh.product_id,pb.id

                                                            ) a

                                                           left join

                                       (
                                       select aal.product_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale,
                                       round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as cccst

                                         from
                                       account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                                       where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                                       and  aa.company_id= %s group by aal.product_id

                                                           ) b

                                                         on a.id=b.product_id

                                                         left join
                                       (

                                       select aaal.product_id ,sum(aaal.price_subtotal) as purtotal,sum(quantity) as quantitypur ,
                                       round(SUM(aaal.price_subtotal_taxinc/ nullif (aaal.quantity,0)),2) as cscst 
                           from
                                       account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                                       where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
                                       and  aaa.company_id= %s
                                         group by aaal.product_id) c

                                       on c.product_id=a.id

                                                   left join

                       (
                                       select pp.brand_id,max(pb.name),pol.product_id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                        from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                        left join product_product as pp on(pp.id=pol.product_id)
                                       left join product_template pt on (pt.id=pp.product_tmpl_id)
                                       left join product_brand as pb on (pb.id=pp.brand_id) 

                                        where
                                        po.state in  ('done', 'paid','invoiced')
                                       and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and %s
                                       and pol.company_id= %s
                                       group by pol.product_id,pp.brand_id)f on a.id=f.product_id)dd 


                                   '''

        self.env.cr.execute(query, (company_id, date_start, date_end, company_id, date_start, date_end, company_id
                                    , date_start, date_end, company_id
                                    ))

        for row in self.env.cr.dictfetchall():
            sale = 0
            possale = 0
            purtotal = 0
            sale = row['sale_total'] if row['sale_total'] else 0
            possale = row['salepos_total'] if row['salepos_total'] else 0
            purtotal = row['purtotal'] if row['purtotal'] else 0
            totalsale = sale + possale
            totalsaleqty = row['salequantity'] if row['salequantity'] else 0
            totalposqty = row['posquantity'] if row['posquantity'] else 0
            quantitypur = row['quantitypur'] if row['quantitypur'] else 0

            res = {
                'sl_no': row['slno'],
                'id': row['id'],
                'pname': row['pname'] if row['pname'] else '',
                'bname': row['dname'] if row['dname'] else '',
                'sale': sale,
                'possale': possale,
                'purtotal': purtotal,
                'totalsale': totalsale,
                'totalsaleqty': totalsaleqty,
                'totalposqty ': totalposqty,
                'sqty': totalsaleqty + totalposqty,
                'quantitypur': quantitypur
            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []
    # def get_brand(self, data, config_id):
    #     lines = []
    #     product = []
    #     average_cost = 0
    #     date_start = data['form']['date_start']
    #     date_end = data['form']['date_end']
    #     company_id = data['form']['company_id']
    #     brand_id = data['form']['brand_id']
    #     brand_only = data['form']['brand_only']
    #
    #     sl = 0
    #
    #     if brand_only:
    #         query = '''
    #
    #          select ROW_NUMBER() OVER(ORDER BY dd.id ASC) AS slno,
    #                         dd.id as id,dd.salepos_total as salepos_total ,dd.sale_total as sale_total,dd.purtotal as purtotal,
    #
    #                          dd.quantitypos as posquantity,
    #                          dd.quantitysale as salequantity,
    #                          dd.quantitypur as quantitypur,
    #                          dd.name as dname,
    #                          dd.productname as pname
    #
    #                         from
    #                         (
    #
    #                         (
    #
    #
    #
    #          select sh.product_id as id,max(pb.name) as name,pb.id as pb,max(pt.name) as productname
    #                       ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation,
    #                       round(COALESCE(SUM(sm.price_unit * sm.product_qty),0)) as ion
    #
    #
    #                      from stock_history  as sh
    #                          left join product_product as pp on(pp.id=sh.product_id)
    #                      left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                      left join product_brand as pb on (pb.id=pp.brand_id)
    #                      left join stock_move as sm on(sm.product_id = pp.id)
    #
    #
    #                     where  sh.company_id=%s and pb.id = %s group by
    #                                             sh.product_id,pb.id
    #
    #                                              ) a
    #
    #                                             left join
    #
    #                         (
    #                         select aal.product_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale,
    #                         round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as cccst
    #
    #                           from
    #                         account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
    #                         where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
    #                         and  aa.company_id= %s group by aal.product_id
    #
    #                                             ) b
    #
    #                                           on a.id=b.product_id
    #
    #                                           left join
    #                         (
    #
    #                         select aaal.product_id ,sum(aaal.price_subtotal) as purtotal,sum(quantity) as quantitypur ,
    #                         round(SUM(aaal.price_subtotal_taxinc/ nullif (aaal.quantity,0)),2) as cscst
    #         	from
    #                         account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    #                         where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
    #                         and  aaa.company_id= %s
    #                           group by aaal.product_id) c
    #
    #                         on c.product_id=a.id
    #
    #                                     left join
    #
    #         (
    #                         select pp.brand_id,max(pb.name),pol.product_id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
    #                          from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
    #                          left join product_product as pp on(pp.id=pol.product_id)
    #                         left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                         left join product_brand as pb on (pb.id=pp.brand_id)
    #
    #                          where
    #                          po.state in  ('done', 'paid','invoiced')
    #                         and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and %s
    #                         and pol.company_id= %s
    #                         group by pol.product_id,pp.brand_id)f on a.id=f.product_id)dd
    #
    #                                                '''
    #         self.env.cr.execute(query, (
    #             date_start, date_end, company_id, (config_id), date_start, date_end, company_id,
    #             date_start, date_end, company_id,
    #         ))
    #         for row in self.env.cr.dictfetchall():
    #             sale = 0
    #             possale = 0
    #             purtotal = 0
    #             sale = row['sale_total'] if row['sale_total'] else 0
    #             possale = row['salepos_total'] if row['salepos_total'] else 0
    #             purtotal = row['purtotal'] if row['purtotal'] else 0
    #             totalsale = sale + possale
    #             totalsaleqty = row['salequantity'] if row['salequantity'] else 0
    #             totalposqty = row['posquantity'] if row['posquantity'] else 0
    #             quantitypur = row['quantitypur'] if row['quantitypur'] else 0
    #
    #             res = {
    #                 'sl_no': row['slno'],
    #                 'id': row['id'],
    #                 'bname': row['dname'] if row['dname'] else '',
    #                 'pname': row['pname'] if row['pname'] else '',
    #                 'sale': sale,
    #                 'possale': possale,
    #                 'purtotal': purtotal,
    #                 'totalsale': totalsale,
    #                 'totalsaleqty': totalsaleqty,
    #                 'totalposqty ': totalposqty,
    #                 'sqty': totalsaleqty + totalposqty,
    #                 'quantitypur': quantitypur
    #             }
    #
    #             lines.append(res)
    #
    #         if lines:
    #             return lines
    #         else:
    #             return []



    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Brand'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 20)
        sheet.set_column(6, 6, 20)
        sheet.set_column(7, 7, 20)
        sheet.set_column(8, 8, 20)
        sheet.set_column(9, 9, 20)
        sheet.set_column(10, 10, 20)
        sheet.set_column(11, 11, 20)
        sheet.set_column(12, 12, 20)
        sheet.set_column(13, 13, 20)
        sheet.set_column(14, 14, 20)
        sheet.set_column(15, 15, 20)
        sheet.set_column(16, 16, 20)
        sheet.set_column(17, 17, 20)
        sheet.set_column(18, 18, 20)
        sheet.set_column(19, 19, 20)
        sheet.set_column(20, 20, 20)

        date_start = data['form']['date_start']

        date_end = data['form']['date_end']
        brand_id = data['form']['brand_id']
        brand_only = data['form']['brand_only']

        # vendor_name = self.env["res.partner"].browse(vendor_id).name

        company = self.env['res.company'].browse(data['form']['company_id']).name

        company_address = self.env['res.company'].browse(data['form']['company_id']).street


        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True})

        format11 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center', 'bold': True})
        yellow_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': 'fcf22f'})

        orange_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': 'f4a442'})

        green_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': '32CD32'})

        blue_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': 'ffffff', 'bg_color': '483D8B'})

        blue_mark2 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca', 'align': 'center'})

        blue_mark3 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 18, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca', 'align': 'center'})

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        # if brand_id:

        sheet.merge_range('A1:G1', company, blue_mark3)
        sheet.merge_range('A2:G2', company_address, blue_mark2)
        sheet.merge_range('A3:G3', "Brand Wise Report ", blue_mark2)
        sheet.merge_range('A4:G4', 'From ' + date_object_date_start.strftime(
            '%d-%m-%Y') + ' - To ' + date_object_date_end.strftime('%d-%m-%Y'), blue_mark2)
        # sheet.merge_range('A5:G5', "VENDOR NAME :- "+  vendor_name, blue_mark2)

        sheet.write('A7', "Sl No", blue_mark)
        sheet.write('B7', "Product Name", blue_mark)

        sheet.write('C7', "Brand", blue_mark)
        sheet.write('D7', "Sale Quantity", blue_mark)
        sheet.write('E7', "Sale Amount", blue_mark)
        sheet.write('F7', "Purchase Quantity", blue_mark)
        sheet.write('G7', "Purchase Amount", blue_mark)
        # sheet.write('G7', "Profit", blue_mark)

        # config = self.env['product.brand'].browse(brand_only)
        # for pfg in config:

        linw_row = 7

        line_column = 0

        # if self.get_brand(data, pfg.id):



        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['pname'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['bname'], font_size_8)

            sheet.write(linw_row, line_column + 3, line['sqty'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['totalsale'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['quantitypur'], font_size_8)
            sheet.write(linw_row, line_column + 6, line['purtotal'], font_size_8)
            # sheet.write(linw_row, line_column + 6, line['profit'], font_size_8)

            linw_row = linw_row + 1
            line_column = 0





        for line in self.get_brand(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['pname'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['bname'], font_size_8)

            sheet.write(linw_row, line_column + 3, line['sqty'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['totalsale'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['quantitypur'], font_size_8)
            sheet.write(linw_row, line_column + 6, line['purtotal'], font_size_8)
            # sheet.write(linw_row, line_column + 6, line['profit'], font_size_8)

            linw_row = linw_row + 1
            line_column = 0

        line_column = 0

        sheet.write(linw_row, 1, "TOTAL", format1)

        total_cell_range12 = xl_range(3, 3, linw_row - 1, 3)
        total_cell_range11 = xl_range(3, 4, linw_row - 1, 4)
        total_cell_range = xl_range(3, 5, linw_row - 1, 5)
        total_cell_range_one = xl_range(3, 6, linw_row - 1, 6)
        # total_cell_range_three = xl_range(3, 6, linw_row - 1, 6)


        sheet.write_formula(linw_row, 3, '=SUM(' + total_cell_range12 + ')', format1)
        sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 5, '=SUM(' + total_cell_range + ')', format1)
        sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_one + ')', format1)
        # sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_three + ')', format1)


Brandrwise('report.brandsale_report_xls.qlty_brand_xls.xlsx', 'sale.order')
