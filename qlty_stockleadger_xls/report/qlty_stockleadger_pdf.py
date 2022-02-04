# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Reportstockleadger(models.AbstractModel):

    _name = 'report.qlty_stockleadger_xls.stockleadger_report_pdf'

    def get_lines(self, data):
        lines = []
        product = []
        average_cost = 0
        product_ids = data['form']['product_ids']
        categ_ids = data['form']['categ_ids']
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        sl = 0

        query = '''
                              select
                              dd.id as id,dd.pname as pname,
                              dd.categ as categ,
                              dd.salepos_total as salepos_total ,
                              dd.sale_total as sale_total,
                              dd.onhand as onhand,
                              dd.valuation as valuation,
                              dd.quantitypos as posquantity,dd.quantitysale as salequantity,dd.salecost as salecost,
                              dd.quantitypur as quantitypur
                              ,dd.pur_total as pur_total
                               from (
                              (
                                    select sh.product_id as id ,pt.name as pname, sum (sh.quantity) as onhand,
                                    pc.id as categ,
                                    round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                                    from stock_history as sh
                               left join product_product as pp on(pp.id=sh.product_id)
                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                               left join product_category pc on (pc.id=pt.categ_id)
                                where  sh.company_id = %s
                                  group by sh.product_id,pt.name
                                  , pc.id
                                   ) a
                                                              left join
                              (
                              select aal.product_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale
                               from
                              account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                           left join product_product as pp on(pp.id=aal.product_id)
                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                              where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                              and  aa.company_id= %s
                             group by aal.product_id
                             ) b
                                                            on a.id=b.product_id
                                                            left join
                              (
                              select aaal.product_id ,sum(aaal.price_subtotal) as pur_total,sum(quantity) as quantitypur from
                              account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                          left join product_product as pp on(pp.id=aaal.product_id)
                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                              where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between  %s and %s
                              and  aaa.company_id= %s
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
                              and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and %s
                               and pol.company_id= %s

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
                                and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between  %s and %s and
                                sh.company_id = %s
                                  group by pt.id

                                  ) f
                                                              on a.id=f.product_id

                          left join
                      (
                      with pos as(
                      select
                      ddd.product_id ,
                      ddd.categ_id,
                      ddd.valuation,
                      ddd.totalquantitysale,
                      ddd.avg
                       from
                      (
                      (
                      select a.product_id as product_id,
                      a.categ_id,
                      a.quantity,
                      a.valuation
                       from (
                          select pc.name as psname,max(sh.product_categ_id) as categ_id,max(sh.product_id) as product_id,sum(sh.quantity) as quantity,
                          round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                              from stock_history sh left join product_template p on (p.id = sh.product_template_id)
                              left join product_category pc on (pc.id=sh.product_categ_id) where
                                available_in_pos = True  group by sh.product_id,pc.name,sh.product_categ_id order by max(sh.product_id)
                                ) a where  a.quantity <0
                      ) aa
                      left join
                      (
                      Select
                      COALESCE(product_id ,product_ids )as product_ids,

                      (COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) as totalsale,
                        (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantitysale,
                      round((COALESCE  ((COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) /   (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) )),0) as avg
                       from
                        (
                                (
                                select DISTINCT(aal.product_id),sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale from account_invoice aaa left join
                                 account_invoice_line aal  on   (aaa.id=aal.invoice_id)
                                   where aaa.type ='out_invoice' and aaa.state in  ('open', 'paid') group by aal.product_id order by   aal.product_id
                                   )  a
                       full join
                                  (
                                  select DISTINCT(pol.product_id ) product_ids ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                               from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                               left join product_product as pp on(pp.id=pol.product_id)
                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                               where
                               po.state in  ('done', 'paid','invoiced') group by pol.product_id order by  pol.product_id
                                ) b
                               on a.product_id =b.product_ids  ) dd where
                             dd.quantitypos !=0
                      ) bb on aa.product_id = bb.product_ids  ) ddd  )
                      select product_id,
                      totalquantitysale,
                       avg
                       from pos
                      ) g   on a.id=g.product_id
                              ) as dd 

                          '''

        if categ_ids and not product_ids:
            query = query + ''' where dd.categ in %s order by dd.pname '''

            self.env.cr.execute(query, (company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    tuple(categ_ids),
                                    ))
        elif not categ_ids and  product_ids:
            query = query + ''' where dd.id in %s order by dd.pname '''

            self.env.cr.execute(query, (company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    tuple(product_ids),
                                    ))

        elif categ_ids and  product_ids:
            query = query + ''' where dd.categ in %s and dd.id in %s order by dd.pname '''

            self.env.cr.execute(query, (company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    tuple(categ_ids),
                                    tuple(product_ids),
                                    ))
        else:

            self.env.cr.execute(query, (company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    ))

        for row in self.env.cr.dictfetchall():
            sl = sl + 1

            sale = 0
            possale = 0
            purtotal = 0
            sale = row['sale_total'] if row['sale_total'] else 0
            purtotalqty = row['sale_total'] if row['sale_total'] else 0
            possale = row['salepos_total'] if row['salepos_total'] else 0
            purtotal = row['pur_total'] if row['pur_total'] else 0
            onhand = row['onhand'] if row['onhand'] else 0
            onhandtotal = row['valuation'] if row['valuation'] else 0
            totalsale = sale + possale
            totalsaleqty = row['salequantity'] if row['salequantity'] else 0
            totalposqty = row['posquantity'] if row['posquantity'] else 0
            totalsaleqty = totalsaleqty + totalposqty
            quantitypur = row['quantitypur'] if row['quantitypur'] else 0

            res = {
                'sl_no': sl,
                'id': row['id'],
                'pname': row['pname'] if row['pname'] else '',
                'pur_total': round(purtotal, 0),
                'quantitypur': round(quantitypur, 0),
                'totalsaleqty': round(totalsaleqty, 0),
                'sale_total': round(totalsale, 0),
                'onhand': round(onhand, 0),
                'onhandtotal': round(onhandtotal, 0),

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
        valuesone = self.get_lines(data)
        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'date_end': date_object_date_end.strftime('%d-%m-%Y'),
            'data': data['form'],
            'time': time,
            'valuesone': valuesone,
        }

        return self.env['report'].render('qlty_stockleadger_xls.stockleadger_report_pdf', docargs)
