from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from odoo.tools.translate import _
from datetime import datetime


class Qltyfastsale(ReportXlsx):

    def get_lines(self, data):

        lines = []
        slno =  0
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        category_id = data['form']['category_id']
        selectiontype = data['form']['selectiontype']
        fstorslw = data['form']['fstorslw']
        countamount = data['form']['countamount']


        if not category_id and selectiontype == 'qty' and fstorslw == 'fst':
            query = '''
                select
                ddd.pname,
                ddd.totalsale as totalsale,
                ddd.totalquantity
                from (
                  select
                        dd.pname as pname,
                        dd.salecost as salecost,
                        dd.salepos_total as salepos_total ,
                        dd.sale_total as sale_total,
                        (COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) as totalsale,
                         dd.quantitypos as posquantity,
                        dd.quantitysale as salequantity,
                        (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantity
                         from
                        (
                        (
                    select pp.id as ids ,pt.name as pname, sum (sh.quantity) as onhand,
                    round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                     from stock_history as sh
                         left join product_product as pp on(pp.id=sh.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                         left join product_category pc on (pc.id=pt.categ_id)
                          where
                          sh.company_id = %s and
                          available_in_pos = True
                            group by pp.id,pt.name
                             ) a
                                                        left join
                        (
                        select  pp.id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale from
                        account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                     left join product_product as pp on(pp.id=aal.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                        where aa.type ='out_invoice' and aa.state in  ('open', 'paid')
                       and to_char(date_trunc('day',aa.date_invoice),'YYYY-MM-DD')::date between %s and %s
                             and  aa.company_id=%s
                                  group by   pp.id
                       ) b
                                                      on a.ids=b.id

                                    left join
                        (
                        select   pp.id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                         from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                         left join product_product as pp on(pp.id=pol.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                         where
                         po.state in  ('done', 'paid','invoiced')
                       and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
                       and pol.company_id= %s
                         group by   pp.id
                            ) d
                                                        on a.ids=d.id
                                                        left join
                                                        (
                                                        select pp.id  ,sum (sh.quantity) as onhands,
                                                        round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),0)) as salecost
                     from stock_history as sh
                         left join product_product as pp on(pp.id=sh.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                         left join product_category pc on (pc.id=pt.categ_id)
                          where  available_in_pos =True
                          and sh.quantity < 0
                          and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between %s and %s
                          and sh.company_id = %s
                            group by  pp.id
                                                        ) f on a.ids =f.id
                        ) as dd ) as ddd order by ddd.totalquantity desc limit %s

                       '''

            self.env.cr.execute(query, (company_id,date_start,date_end,company_id,date_start,date_end,
                                        company_id,date_start, date_end,company_id,countamount))

            for row in self.env.cr.dictfetchall():
                slno = slno + 1
                res = {
                    'sl_no':slno,
                    'pname': row['pname'] if row['pname'] else '',
                    'sale_total':row['totalsale'] ,
                    'totalquantity': row['totalquantity']
                }
                lines.append(res)

        if not category_id and selectiontype == 'amt' and fstorslw == 'fst'  :

            query = '''
                select
                ddd.pname,
                ddd.totalsale as totalsale,
                ddd.totalquantity
                from (
                  select
                        dd.pname as pname,
                        dd.salecost as salecost,
                        dd.salepos_total as salepos_total ,
                        dd.sale_total as sale_total,
                        (COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) as totalsale,
                         dd.quantitypos as posquantity,
                        dd.quantitysale as salequantity,
                        (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantity
                         from
                        (
                        (
                    select pp.id as ids ,pt.name as pname, sum (sh.quantity) as onhand,
                    round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                     from stock_history as sh
                         left join product_product as pp on(pp.id=sh.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                         left join product_category pc on (pc.id=pt.categ_id)
                          where
                          sh.company_id = %s and
                          available_in_pos = True
                            group by pp.id,pt.name
                             ) a
                                                        left join
                        (
                        select  pp.id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale from
                        account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                     left join product_product as pp on(pp.id=aal.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                        where aa.type ='out_invoice' and aa.state in  ('open', 'paid')
                       and to_char(date_trunc('day',aa.date_invoice),'YYYY-MM-DD')::date between %s and %s
                             and  aa.company_id=%s
                                  group by   pp.id
                       ) b
                                                      on a.ids=b.id

                                    left join
                        (
                        select   pp.id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                         from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                         left join product_product as pp on(pp.id=pol.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                         where
                         po.state in  ('done', 'paid','invoiced')
                       and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
                       and pol.company_id= %s
                         group by   pp.id
                            ) d
                                                        on a.ids=d.id
                                                        left join
                                                        (
                                                        select pp.id  ,sum (sh.quantity) as onhands,
                                                        round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),0)) as salecost
                     from stock_history as sh
                         left join product_product as pp on(pp.id=sh.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                         left join product_category pc on (pc.id=pt.categ_id)
                          where  available_in_pos =True
                          and sh.quantity < 0
                          and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between %s and %s
                          and sh.company_id = %s
                            group by  pp.id       ) f on a.ids =f.id
                        ) as dd ) as ddd order by ddd.totalsale desc limit %s

                       '''

            self.env.cr.execute(query, (company_id,date_start,date_end,company_id,date_start,date_end,
                                        company_id,date_start, date_end,company_id,countamount))
            for row in self.env.cr.dictfetchall():
                slno = slno + 1
                res = {
                    'sl_no':slno,
                    'pname': row['pname'] if row['pname'] else '',
                    'sale_total':row['totalsale'] ,
                    'totalquantity': row['totalquantity']
                }
                lines.append(res)




        if category_id and selectiontype == 'qty' and fstorslw == 'fst':

            query = '''


		        select
                ddd.pname,
                ddd.categ_id ,
                ddd.totalsale,
                ddd.totalquantity
                from (
                  select
                        dd.pname as pname,

                        dd.categ_id as  categ_id,
                        dd.onhand as onhand,
                        dd.valuation as valuation,
                        dd.salecost as salecost,
                        dd.salepos_total as salepos_total ,
                        dd.sale_total as sale_total,
                        (COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) as totalsale,
                         dd.quantitypos as posquantity,
                        dd.quantitysale as salequantity,
                        (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantity
                         from
                        (
                        (
                    select pp.id as ids ,pt.name as pname,pt.categ_id as categ_id , sum (sh.quantity) as onhand,
                    round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                     from stock_history as sh
                         left join product_product as pp on(pp.id=sh.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                         left join product_category pc on (pc.id=pt.categ_id)
                          where  sh.company_id = %s and available_in_pos =True
                            group by pp.id,pt.name,pt.categ_id
                             ) a

                                                        left join
                        (
                        select  pp.id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale from
                        account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                     left join product_product as pp on(pp.id=aal.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)

                        where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between  %s and  %s
                                and  aa.company_id=  %s      group by   pp.id

                       ) b

                                                      on a.ids=b.id

                                    left join
                        (
                        select   pp.id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                         from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                         left join product_product as pp on(pp.id=pol.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                         where
                         po.state in  ('done', 'paid','invoiced')
                        and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and   %s
                         and pol.company_id=  %s
                         group by   pp.id
                            ) d
                                                        on a.ids=d.id
                                                        left join
                                                        (
                                                        select pp.id  ,sum (sh.quantity) as onhands,
                                                        round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),0)) as salecost
                     from stock_history as sh
                         left join product_product as pp on(pp.id=sh.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                         left join product_category pc on (pc.id=pt.categ_id)
                          where  available_in_pos =True
                          and sh.quantity <0
                          and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between  %s and   %s
                           and sh.company_id =  %s
                            group by  pp.id
                        ) f on a.ids =f.id
                        ) as dd ) as ddd where ddd.categ_id =  %s order by ddd.totalquantity desc limit  %s

                                                                '''

            self.env.cr.execute(query, (company_id, date_start, date_end, company_id, date_start, date_end,
                                        company_id, date_start, date_end, company_id,category_id, countamount))
            for row in self.env.cr.dictfetchall():
                slno = slno + 1
                res = {
                    'sl_no': slno,
                    'pname': row['pname'] if row['pname'] else '',
                    'sale_total': row['totalsale'],
                    'totalquantity': row['totalquantity']
                }
                lines.append(res)

        if category_id and selectiontype == 'amt' and fstorslw == 'fst' :

            query = '''

            select
            ddd.pname,
            ddd.categ_id ,
            ddd.totalsale,
            ddd.totalquantity
            from (
              select
                    dd.pname as pname,

                    dd.categ_id as  categ_id,
                    dd.onhand as onhand,
                    dd.valuation as valuation,
                    dd.salecost as salecost,
                    dd.salepos_total as salepos_total ,
                    dd.sale_total as sale_total,
                    (COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) as totalsale,
                     dd.quantitypos as posquantity,
                    dd.quantitysale as salequantity,
                    (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantity
                     from
                    (
                    (
                select pp.id as ids ,pt.name as pname,pt.categ_id as categ_id , sum (sh.quantity) as onhand,
                round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                 from stock_history as sh
                     left join product_product as pp on(pp.id=sh.product_id)
                     left join product_template pt on (pt.id=pp.product_tmpl_id)
                     left join product_category pc on (pc.id=pt.categ_id)
                      where  sh.company_id = %s and available_in_pos =True
                        group by pp.id,pt.name,pt.categ_id
                         ) a

                                                    left join
                    (
                    select  pp.id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale from
                    account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                 left join product_product as pp on(pp.id=aal.product_id)
                     left join product_template pt on (pt.id=pp.product_tmpl_id)

                    where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between  %s and  %s
                            and  aa.company_id=  %s      group by   pp.id

                   ) b

                                                  on a.ids=b.id

                                left join
                    (
                    select   pp.id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                     from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                     left join product_product as pp on(pp.id=pol.product_id)
                     left join product_template pt on (pt.id=pp.product_tmpl_id)
                     where
                     po.state in  ('done', 'paid','invoiced')
                    and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and   %s
                     and pol.company_id=  %s
                     group by   pp.id
                        ) d
                                                    on a.ids=d.id
                                                    left join
                                                    (
                                                    select pp.id  ,sum (sh.quantity) as onhands,
                                                    round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),0)) as salecost
                 from stock_history as sh
                     left join product_product as pp on(pp.id=sh.product_id)
                     left join product_template pt on (pt.id=pp.product_tmpl_id)
                     left join product_category pc on (pc.id=pt.categ_id)
                      where  available_in_pos =True
                      and sh.quantity <0
                      and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between  %s and   %s
                       and sh.company_id =  %s
                        group by  pp.id
                    ) f on a.ids =f.id
                    ) as dd ) as ddd where ddd.categ_id =  %s order by ddd.totalsale desc limit  %s

                                                                            '''

            self.env.cr.execute(query, (company_id, date_start, date_end, company_id, date_start, date_end,
                                        company_id, date_start, date_end, company_id, category_id, countamount))
            for row in self.env.cr.dictfetchall():
                slno = slno + 1
                res = {
                    'sl_no': slno,
                    'pname': row['pname'] if row['pname'] else '',
                    'sale_total': row['totalsale'],
                    'totalquantity': row['totalquantity']
                }
                lines.append(res)


        if not category_id and selectiontype == 'qty' and fstorslw == 'slw':
            query = '''
            
                        select
                       ddd.pname,
                       ddd.totalsale as totalsale,
                       ddd.totalquantity
                       from (
                         select
                               dd.pname as pname,
                               dd.salecost as salecost,
                               dd.salepos_total as salepos_total ,
                               dd.sale_total as sale_total,
                               (COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) as totalsale,
                                dd.quantitypos as posquantity,
                               dd.quantitysale as salequantity,
                               (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantity
                                from
                               (
                               (
                           select pp.id as ids ,pt.name as pname, sum (sh.quantity) as onhand,
                           round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                            from stock_history as sh
                                left join product_product as pp on(pp.id=sh.product_id)
                                left join product_template pt on (pt.id=pp.product_tmpl_id)
                                left join product_category pc on (pc.id=pt.categ_id)
                                 where
                                 sh.company_id = %s and
                                 available_in_pos = True
                                   group by pp.id,pt.name
                                    ) a
                                                               left join
                               (
                               select  pp.id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale from
                               account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                            left join product_product as pp on(pp.id=aal.product_id)
                                left join product_template pt on (pt.id=pp.product_tmpl_id)
                               where aa.type ='out_invoice' and aa.state in  ('open', 'paid')
                              and to_char(date_trunc('day',aa.date_invoice),'YYYY-MM-DD')::date between %s and %s
                                    and  aa.company_id= %s
                                         group by   pp.id
                              ) b
                                                             on a.ids=b.id

                                           left join
                               (
                               select   pp.id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                left join product_product as pp on(pp.id=pol.product_id)
                                left join product_template pt on (pt.id=pp.product_tmpl_id)
                                where
                                po.state in  ('done', 'paid','invoiced')
                              and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
                              and pol.company_id=  %s
                                group by   pp.id
                                   ) d
                                                               on a.ids=d.id
                                                               left join
                                                               (
                                                               select pp.id  ,sum (sh.quantity) as onhands,
                                                               round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),0)) as salecost
                            from stock_history as sh
                                left join product_product as pp on(pp.id=sh.product_id)
                                left join product_template pt on (pt.id=pp.product_tmpl_id)
                                left join product_category pc on (pc.id=pt.categ_id)
                                 where  available_in_pos =True
                                 and sh.quantity < 0
                                 and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between %s and %s
                                 and sh.company_id = %s
                                   group by  pp.id
                                                               ) f on a.ids =f.id
                               ) as dd ) as ddd where ddd.totalquantity > 0  order by ddd.totalquantity asc limit %s
                      
                              '''

            self.env.cr.execute(query, (company_id, date_start, date_end, company_id, date_start, date_end,
                                        company_id, date_start, date_end, company_id, countamount))

            for row in self.env.cr.dictfetchall():
                slno = slno + 1
                res = {
                    'sl_no': slno,
                    'pname': row['pname'] if row['pname'] else '',
                    'sale_total': row['totalsale'],
                    'totalquantity': row['totalquantity']
                }
                lines.append(res)


        if not category_id and selectiontype == 'amt' and fstorslw == 'slw':
            query = '''

                        select
                       ddd.pname,
                       ddd.totalsale as totalsale,
                       ddd.totalquantity
                       from (
                         select
                               dd.pname as pname,
                               dd.salecost as salecost,
                               dd.salepos_total as salepos_total ,
                               dd.sale_total as sale_total,
                               (COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) as totalsale,
                                dd.quantitypos as posquantity,
                               dd.quantitysale as salequantity,
                               (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantity
                                from
                               (
                               (
                           select pp.id as ids ,pt.name as pname, sum (sh.quantity) as onhand,
                           round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                            from stock_history as sh
                                left join product_product as pp on(pp.id=sh.product_id)
                                left join product_template pt on (pt.id=pp.product_tmpl_id)
                                left join product_category pc on (pc.id=pt.categ_id)
                                 where
                                 sh.company_id = %s and
                                 available_in_pos = True
                                   group by pp.id,pt.name
                                    ) a
                                                               left join
                               (
                               select  pp.id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale from
                               account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                            left join product_product as pp on(pp.id=aal.product_id)
                                left join product_template pt on (pt.id=pp.product_tmpl_id)
                               where aa.type ='out_invoice' and aa.state in  ('open', 'paid')
                              and to_char(date_trunc('day',aa.date_invoice),'YYYY-MM-DD')::date between %s and %s
                                    and  aa.company_id= %s
                                         group by   pp.id
                              ) b
                                                             on a.ids=b.id

                                           left join
                               (
                               select   pp.id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                left join product_product as pp on(pp.id=pol.product_id)
                                left join product_template pt on (pt.id=pp.product_tmpl_id)
                                where
                                po.state in  ('done', 'paid','invoiced')
                              and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
                              and pol.company_id=  %s
                                group by   pp.id
                                   ) d
                                                               on a.ids=d.id
                                                               left join
                                                               (
                                                               select pp.id  ,sum (sh.quantity) as onhands,
                                                               round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),0)) as salecost
                            from stock_history as sh
                                left join product_product as pp on(pp.id=sh.product_id)
                                left join product_template pt on (pt.id=pp.product_tmpl_id)
                                left join product_category pc on (pc.id=pt.categ_id)
                                 where  available_in_pos =True
                                 and sh.quantity < 0
                                 and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between %s and %s
                                 and sh.company_id = %s
                                   group by  pp.id
                                                               ) f on a.ids =f.id
                               ) as dd ) as ddd where ddd.totalquantity > 0 and ddd.totalsale >0  
                               order by ddd.totalsale asc limit %s

                              '''

            self.env.cr.execute(query, (company_id, date_start, date_end, company_id, date_start, date_end,
                                        company_id, date_start, date_end, company_id, countamount))

            for row in self.env.cr.dictfetchall():
                slno = slno + 1
                res = {
                    'sl_no': slno,
                    'pname': row['pname'] if row['pname'] else '',
                    'sale_total': row['totalsale'],
                    'totalquantity': row['totalquantity']
                }
                lines.append(res)

        if category_id and selectiontype == 'qty' and fstorslw == 'slw':

            query = '''
        		        select
                        ddd.pname,
                        ddd.categ_id ,
                        ddd.totalsale,
                        ddd.totalquantity
                        from (
                          select
                                dd.pname as pname,

                                dd.categ_id as  categ_id,
                                dd.onhand as onhand,
                                dd.valuation as valuation,
                                dd.salecost as salecost,
                                dd.salepos_total as salepos_total ,
                                dd.sale_total as sale_total,
                                (COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) as totalsale,
                                 dd.quantitypos as posquantity,
                                dd.quantitysale as salequantity,
                                (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantity
                                 from
                                (
                                (
                            select pp.id as ids ,pt.name as pname,pt.categ_id as categ_id , sum (sh.quantity) as onhand,
                            round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                             from stock_history as sh
                                 left join product_product as pp on(pp.id=sh.product_id)
                                 left join product_template pt on (pt.id=pp.product_tmpl_id)
                                 left join product_category pc on (pc.id=pt.categ_id)
                                  where  sh.company_id = %s and available_in_pos =True
                                    group by pp.id,pt.name,pt.categ_id
                                     ) a

                                                                left join
                                (
                                select  pp.id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale from
                                account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                             left join product_product as pp on(pp.id=aal.product_id)
                                 left join product_template pt on (pt.id=pp.product_tmpl_id)

                                where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between  %s and  %s
                                        and  aa.company_id=  %s      group by   pp.id

                               ) b

                                                              on a.ids=b.id

                                            left join
                                (
                                select   pp.id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                 from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                 left join product_product as pp on(pp.id=pol.product_id)
                                 left join product_template pt on (pt.id=pp.product_tmpl_id)
                                 where
                                 po.state in  ('done', 'paid','invoiced')
                                and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and   %s
                                 and pol.company_id=  %s
                                 group by   pp.id
                                    ) d
                                                                on a.ids=d.id
                                                                left join
                                                                (
                                                                select pp.id  ,sum (sh.quantity) as onhands,
                                                                round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),0)) as salecost
                             from stock_history as sh
                                 left join product_product as pp on(pp.id=sh.product_id)
                                 left join product_template pt on (pt.id=pp.product_tmpl_id)
                                 left join product_category pc on (pc.id=pt.categ_id)
                                  where  available_in_pos =True
                                  and sh.quantity <0
                                  and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between  %s and   %s
                                   and sh.company_id =  %s
                                    group by  pp.id
                                ) f on a.ids =f.id
                                ) as dd ) as ddd where ddd.categ_id =  %s and ddd.totalquantity > 0
                                 order by ddd.totalquantity asc limit  %s

                                                                        '''

            self.env.cr.execute(query, (company_id, date_start, date_end, company_id, date_start, date_end,
                                        company_id, date_start, date_end, company_id, category_id, countamount))
            for row in self.env.cr.dictfetchall():
                slno = slno + 1
                res = {
                    'sl_no': slno,
                    'pname': row['pname'] if row['pname'] else '',
                    'sale_total': row['totalsale'],
                    'totalquantity': row['totalquantity']
                }
                lines.append(res)

        if category_id and selectiontype == 'amt' and fstorslw == 'slw':

            query = '''
             		        select
                             ddd.pname,
                             ddd.categ_id ,
                             ddd.totalsale,
                             ddd.totalquantity
                             from (
                               select
                                     dd.pname as pname,

                                     dd.categ_id as  categ_id,
                                     dd.onhand as onhand,
                                     dd.valuation as valuation,
                                     dd.salecost as salecost,
                                     dd.salepos_total as salepos_total ,
                                     dd.sale_total as sale_total,
                                     (COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) as totalsale,
                                      dd.quantitypos as posquantity,
                                     dd.quantitysale as salequantity,
                                     (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantity
                                      from
                                     (
                                     (
                                 select pp.id as ids ,pt.name as pname,pt.categ_id as categ_id , sum (sh.quantity) as onhand,
                                 round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                                  from stock_history as sh
                                      left join product_product as pp on(pp.id=sh.product_id)
                                      left join product_template pt on (pt.id=pp.product_tmpl_id)
                                      left join product_category pc on (pc.id=pt.categ_id)
                                       where  sh.company_id = %s and available_in_pos =True
                                         group by pp.id,pt.name,pt.categ_id
                                          ) a

                                                                     left join
                                     (
                                     select  pp.id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale from
                                     account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                                  left join product_product as pp on(pp.id=aal.product_id)
                                      left join product_template pt on (pt.id=pp.product_tmpl_id)

                                     where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between  %s and  %s
                                             and  aa.company_id=  %s      group by   pp.id

                                    ) b

                                                                   on a.ids=b.id

                                                 left join
                                     (
                                     select   pp.id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                      from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                      left join product_product as pp on(pp.id=pol.product_id)
                                      left join product_template pt on (pt.id=pp.product_tmpl_id)
                                      where
                                      po.state in  ('done', 'paid','invoiced')
                                     and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and   %s
                                      and pol.company_id=  %s
                                      group by   pp.id
                                         ) d
                                                                     on a.ids=d.id
                                                                     left join
                                                                     (
                                                                     select pp.id  ,sum (sh.quantity) as onhands,
                                                                     round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),0)) as salecost
                                  from stock_history as sh
                                      left join product_product as pp on(pp.id=sh.product_id)
                                      left join product_template pt on (pt.id=pp.product_tmpl_id)
                                      left join product_category pc on (pc.id=pt.categ_id)
                                       where  available_in_pos =True
                                       and sh.quantity <0
                                       and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between  %s and   %s
                                        and sh.company_id =  %s
                                         group by  pp.id
                                     ) f on a.ids =f.id
                                     ) as dd ) as ddd where ddd.categ_id =  %s and ddd.totalquantity > 0
                                     and ddd.totalsale >0
                                      order by ddd.totalsale asc limit  %s

                                                                             '''

            self.env.cr.execute(query, (company_id, date_start, date_end, company_id, date_start, date_end,
                                        company_id, date_start, date_end, company_id, category_id, countamount))
            for row in self.env.cr.dictfetchall():
                slno = slno + 1
                res = {
                    'sl_no': slno,
                    'pname': row['pname'] if row['pname'] else '',
                    'sale_total': row['totalsale'],
                    'totalquantity': row['totalquantity']
                }
                lines.append(res)







        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Product'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2,20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 25)
        sheet.set_column(5, 5, 25)
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
        category_id = data['form']['category_id']

        fstorslw = data['form']['fstorslw']

        category_name = self.env["product.category"].browse(category_id).name

        company=self.env['res.company'].browse(data['form']['company_id']).name

        company_address=self.env['res.company'].browse(data['form']['company_id']).street


        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True})

        format2 = workbook.add_format(
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

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        productname = "Product"
        if category_id and fstorslw == 'fst' :
            reportname="Fast Sale Report  " + category_name

        if not category_id and fstorslw == 'fst' :
            reportname = "Fast Sale Report"
        if category_id and fstorslw == 'slw' :
            reportname="Slow Sale Report  " + category_name

        if not category_id and fstorslw == 'slw' :
            reportname = "Slow Sale Report"

        sheet.merge_range('A1:D1', company if company else '', blue_mark3)
        sheet.merge_range('A2:D2', company_address if company_address else '',blue_mark2)
        sheet.merge_range('A3:D3', reportname,blue_mark2)
        sheet.merge_range('A4:D4','From ' + date_object_date_start.strftime('%d-%m-%Y') + ' - To ' + date_object_date_end.strftime('%d-%m-%Y'), blue_mark2)
        sheet.merge_range('A5:D5', category_name if category_name else '',blue_mark2)

        sheet.write('A6', "Sl No", blue_mark)

        sheet.write('B6', productname, blue_mark)
        sheet.write('C6', "Sale Quantity", blue_mark)
        sheet.write('D6', "Sale Amount", blue_mark)





        linw_row = 6
        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['pname'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['totalquantity'], font_size_8)
            sheet.write(linw_row, line_column + 3, line['sale_total'], font_size_8)

            linw_row = linw_row + 1
            line_column = 0

        line_column = 0

        sheet.write(linw_row, 1, "TOTAL", format1)

        total_cell_range11 = xl_range(3, 2, linw_row - 1, 2)
        total_cell_range = xl_range(3, 3, linw_row - 1, 3)
        # total_cell_range_one = xl_range(3, 4, linw_row - 1, 4)
        # total_cell_range_two = xl_range(3, 5, linw_row - 1, 5)
        # total_cell_range_three = xl_range(3, 6, linw_row - 1, 6)
        # total_cell_range_4 = xl_range(3, 7, linw_row - 1, 7)

        sheet.write_formula(linw_row, 2, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 3, '=SUM(' + total_cell_range + ')', format1)
        # sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range_one + ')', format1)
        # sheet.write_formula(linw_row, 5, '=SUM(' + total_cell_range_two + ')', format1)
        # sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_three + ')', format1)
        # sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range_4 + ')', format1)

Qltyfastsale('report.qlty_fastsale_xls.qlty_fastsale_xls.xlsx', 'sale.order')
