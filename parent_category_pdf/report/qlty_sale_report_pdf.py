# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportCategory(models.AbstractModel):

    _name = 'report.parent_category_pdf.parent_category_pdf'

    def get_cash(self, data):

        lines = []
        invoice_id = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        # company_id = data['form']['company_id']
        category_id = data['form']['category_id']
        child_category = data['form']['child_category']
        cat_only = data['form']['cat_only']
        subcategory_id = data['form']['subcategory_id']
        stock_location = data['form']['stock_location']

        cr = 0

        if cat_only == True:

            query21 = '''



                                        select
                                           dd.id as id,dd.pname as pname,
                                           dd.salepos_total as salepos_total ,
                                           dd.sale_total as sale_total,
                                           dd.pur_total as pur_total,
                                           dd.purchase_qty as purchase_qty,
                                           dd.purchase_freeqty as purchase_freeqty,

                                           dd.quantitypos as posquantity,
                                           dd.quantitysale as salequantity


                                            from
                                           (
                                           (

                                   	select pt.categ_id as id ,pc.name as pname, sum (sh.quantity) as onhand,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),2)) as valuation
                                   	 from stock_history as sh
                                            left join product_product as pp on(pp.id=sh.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)
                                            left join product_category pc on (pc.id=pt.categ_id)
                                             where  available_in_pos =True
                                               group by pt.categ_id,pc.name

                                                ) a

                                                                           left join
                                           (
                                           select SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.quantity  ELSE ai.quantity END) as quantitysale,
                                   SUM(round((CASE WHEN a.type = 'out_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END),2)) as sale_total,
                                   max(ai.price_unit) as price_unit,max(sl.complete_name),
                                   pc.id as categ_id,pc.name from account_invoice_line as ai
                                       left join account_invoice as a
                                       on a.id=ai.invoice_id
                                       left join product_product as p
                                       on ai.product_id =p.id
                                       left join product_template as pt
                                       on pt.id = p.product_tmpl_id
                                       left join product_category as pc 
                                       on (pt.categ_id =pc.id)
                                       left join stock_location as sl
                                       on (a.stock_locations=sl.id) 

                                       where a.type in ('out_invoice','out_refund') and a.state in ('open','paid')
                                        and a.date_invoice BETWEEN %s and %s and sl.id=%s
                                       GROUP BY pc.id 

                                          ) b

                                                                         on a.id=b.categ_id
                                                                         left join
                                           (

                                           select  pt.categ_id ,sum(aaal.price_subtotal_taxinc) as pur_total,
                                            SUM(aaal.quantity) as purchase_qty,
                                                               SUM(aaal.free_qty) as purchase_freeqty from
                                           account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                                   	left join product_product as pp on(pp.id=aaal.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)
                                            left join product_category pc on (pc.id=pt.categ_id)
                                            


                                           where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s

                                   	group by  pt.categ_id
                                   	) c
                                           on c.categ_id=a.id
                                           			left join
                                           (
                                           select  pt.categ_id  ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                            from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                            left join product_product as pp on(pp.id=pol.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)
                                            left join product_category pc on (pc.id=pt.categ_id)
                                            left join stock_location as sl on (po.location_id=sl.id) 
                                            where po.invoice_id is NULL and
                                            po.state in  ('done', 'paid','invoiced')
                                           and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s and sl.id=%s

                                            group by  pt.categ_id
                                               ) d
                                                                           on a.id=d.categ_id
                                                                           left join
                                                                           (
                                                                           select pt.categ_id as categ_id ,sum (sh.quantity) as onhands,
                                                                           round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),2)) as salecost1
                                   	 from stock_history as sh
                                            left join product_product as pp on(pp.id=sh.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)
                                            left join product_category pc on (pc.id=pt.categ_id)
                                             where  available_in_pos =True
                                             and sh.quantity <0
                                             and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between %s and %s

                                               group by pt.categ_id

                                                                           ) f on a.id =f.categ_id

                                                                             left join


                                                                              (

                                          select gg.categ_id as categ_id,
                               			sum(gg.salecost) as salecost from( select 
                                           pt.categ_id as categ_id ,
                                           aaal.product_id as product_id,

                                           sum(aaal.price_subtotal)/nullif (sum(aaal.quantity),0) as salecost from
                                           account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                                       left join product_product as pp on(pp.id=aaal.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)


                                           where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s

                                       group by  aaal.product_id,pt.categ_id)gg group by gg.categ_id
                                       ) k on a.id=k.categ_id

                                       left join


                                               (   select sum(ss.onhand*yy.salecost) as onhand1,ss.categ_id as categ_id,
                                               sum(yy.salecost*(cv.quantitypos)) as totalsalecost1,
                                               sum(case when ww.quantitysale is NULL then 0 else ww.quantitysale END)as tt ,
                                               sum(case when cv.quantitypos is NULL then 0 else cv.quantitypos END)as qq,

                                               sum(yy.salecost) ,
                               (sum(yy.salecost*((case when ww.quantitysale is NULL then 0 else ww.quantitysale END)+(case when cv.quantitypos is NULL then 0 else cv.quantitypos END)))) as ttqq,

                                               sum(cv.quantitypos+ww.quantitysale) from  

                                                (select pt.categ_id as categ_id,sh.product_id as id ,pt.name as pname, sum (sh.quantity) as onhand
                                   			  ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),2)) as valuation
                                   			  from stock_history as sh
                                            left join product_product as pp on(pp.id=sh.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)

                                              group by sh.product_id,pt.name,pt.categ_id
                                                )ss
                               			left join


                               			  ( select 
                                           pt.categ_id as categ_id ,
                                           aaal.product_id as product_id,

                                           sum(aaal.price_subtotal)/nullif (sum(aaal.quantity),0) as salecost from
                                           account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                                       left join product_product as pp on(pp.id=aaal.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)


                                           where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s

                                       group by  aaal.product_id,pt.categ_id)yy on ss.id=yy.product_id

                                       left join

                                        (
                                           select pol.product_id as product_id  ,pt.categ_id as categ_id,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                            from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                            left join product_product as pp on(pp.id=pol.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)
                                            left join stock_location as sl on (po.location_id=sl.id) 
                                            
                                            
                                            where po.invoice_id is NULL and
                                            po.state in  ('done', 'paid','invoiced')
                                           and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s and sl.id=%s


                                            group by pol.product_id,pt.categ_id 
                                               )cv on ss.id=cv.product_id

                                               left join

                                               (
                                          select SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.quantity  ELSE ai.quantity END) as quantitysale,
                                   SUM(round((CASE WHEN a.type = 'out_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END),2)) as sale_total,
                                  max(sl.complete_name),ai.product_id as product_id,
                                   pc.id as categ_id,pc.name from account_invoice_line as ai
                                       left join account_invoice as a
                                       on a.id=ai.invoice_id
                                       left join product_product as p
                                       on ai.product_id =p.id
                                       left join product_template as pt
                                       on pt.id = p.product_tmpl_id
                                       left join product_category as pc 
                                       on (pt.categ_id =pc.id)
                                       left join stock_location as sl
                                       on (a.stock_locations=sl.id) 

                                       where a.type in ('out_invoice','out_refund') and a.state in ('open','paid') 
                                       and a.date_invoice BETWEEN %s and %s and
                                       sl.id=%s 
                                       GROUP BY pc.id ,ai.product_id 

                                          ) ww on ww.product_id=ss.id group by ss.categ_id)pk on a.id=pk.categ_id


                                          left join




                                   (



                                   with pos as(
                                   select

                                   ddd.product_id ,
                                   ddd.categ_id,

                                   ddd.valuation,
                                   ddd.quantity,
                                   ddd.avg,
                                   ddd.quantity*ddd.avg as costofsalewithoutpurchase

                                    from

                                   (

                                   (
                                   select a.product_id as product_id,

                                   a.categ_id,
                                   a.quantity,
                                   a.valuation
                                    from (


                                       select pc.name as psname,max(sh.product_categ_id) as categ_id,max(sh.product_id) as product_id,sum(sh.quantity) as quantity,
                                       round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),2)) as valuation
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
                                     (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantity,

                                   round((COALESCE  ((COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) /   (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) )),2) as avg

                                    from

                                     (
                                             (
                                             select DISTINCT(aal.product_id),sum(aal.price_subtotal_taxinc) as sale_total,sum(quantity) as quantitysale from account_invoice aaa left join
                                              account_invoice_line aal  on   (aaa.id=aal.invoice_id)
                                                where aaa.type ='out_invoice' and aaa.state in  ('open', 'paid') group by aal.product_id order by   aal.product_id
                                                )  a

                                    full join
                                               (
                                               select DISTINCT(pol.product_id ) product_ids ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                            from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                            left join product_product as pp on(pp.id=pol.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)
                                            left join product_category pc on (pc.id=pt.categ_id)
                                            where po.invoice_id is NULL and
                                            po.state in  ('done', 'paid','invoiced') group by pol.product_id order by  pol.product_id
                                             ) b
                                            on a.product_id =b.product_ids  ) dd where
                                          dd.quantitypos !=0
                                   ) bb on aa.product_id = bb.product_ids  ) ddd  )
                                   select categ_id,
                                   --sum(valuation) as valuation,
                                   sum(quantity) as quantity,
                                   sum(avg) as avg,
                                   sum(costofsalewithoutpurchase) as costofsalewithoutpurchase

                                    from pos  group by categ_id








                                   ) h on h.categ_id=a.id





                                           ) as dd order by dd.pname








                                                                               '''

            self.env.cr.execute(query21, (
                date_start, date_end,stock_location,
                date_start, date_end,
                date_start, date_end,stock_location,
                date_start, date_end,
                date_start, date_end,
                date_start, date_end,
                date_start, date_end,stock_location,
                date_start, date_end,stock_location

            ))
            for row in self.env.cr.dictfetchall():
                # sl = sl + 1

                sale = 0
                possale = 0
                purtotal = 0

                # poscost = row['poscost'] if row['poscost'] else 0
                sale = row['sale_total'] if row['sale_total'] else 0
                possale = row['salepos_total'] if row['salepos_total'] else 0
                purtotal = row['pur_total'] if row['pur_total'] else 0

                totalsale = sale + possale
                totalsaleqty = row['salequantity'] if row['salequantity'] else 0
                totalposqty = row['posquantity'] if row['posquantity'] else 0


                ph_qty = row['purchase_qty'] if row['purchase_qty'] else 0
                pf_amt = row['purchase_freeqty'] if row['purchase_freeqty'] else 0
                p_qty = ph_qty + pf_amt

                res = {

                    # 'sl_no': sl,
                    'id': row['id'],
                    'pname': row['pname'] if row['pname'] else '',
                    'sale_total': round(totalsale, 2),
                    'pur_total': round(purtotal, 2),

                    'sp_qty': (((totalsaleqty + totalposqty))),
                    'p_qty': p_qty

                }

                lines.append(res)

        if lines:
            return lines
        else:
            return []



    def get_cash_wise(self, data, config_id):
        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        # company_id = data['form']['company_id']
        category_id = data['form']['category_id']
        child_category = data['form']['child_category']
        cat_only = data['form']['cat_only']
        subcategory_id = data['form']['subcategory_id']
        stock_location = data['form']['stock_location']

        # date_start=
        cash = 0

        cr = 0
        cm = 0

        if cat_only==False:
            sl = 0
            pf_amt = 0
            s_amt = 0
            s_qty = 0
            p_qty = 0
            p_amt = 0
            price_u = 0
            # pname=" "

            product = self.env["product.product"].search([])

            for i in product:



                cost = 0
                gross_profit = 0
                gross_profit_per = 0
                quantity = 0
                landingcost = 0
                # pname=" "

                sl += 1
                sale_query = ''' select SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.quantity  ELSE ai.quantity END) as sale_qty,
                                   SUM(round((CASE WHEN a.type = 'out_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END),2)) as sale_amount,
                                   max(ai.price_unit) as price_unit,sl.complete_name,
                                   pc.id,pc.name from account_invoice_line as ai
                                       left join account_invoice as a
                                       on a.id=ai.invoice_id
                                       left join product_product as p
                                       on ai.product_id =p.id
                                       left join product_template as pt
                                       on pt.id = p.product_tmpl_id
                                       left join product_category as pc 
                                       on (pt.categ_id =pc.id)
                                       left join stock_location as sl
                                       on (a.stock_locations=sl.id) 

                                       where a.type in ('out_invoice','out_refund') and a.state in ('open','paid') and
                                       pc.id=%s and sl.id=%s and a.date_invoice BETWEEN %s and %s
                                       GROUP BY pc.id,sl.id  order by sale_qty'''
                self.env.cr.execute(sale_query, (config_id, stock_location,date_start, date_end,))
                for row in self.env.cr.dictfetchall():
                    s_qty += row['sale_qty'] if row['sale_qty'] else 0
                    s_amt += row['sale_amount'] if row['sale_amount'] else 0
                    price_u += row['price_unit'] if row['price_unit'] else 0
                s=self.env['product.category'].browse(config_id).name
                pname = s

                purchase_query = ''' 
                                   select SUM(CASE WHEN a.type = 'in_refund'  then  -1*ai.quantity  ELSE ai.quantity END ) as purchase_qty,
                                            SUM(CASE WHEN a.type = 'in_refund'  then  -1*ai.free_qty  ELSE ai.free_qty END ) as purchase_freeqty,
                                   SUM(CASE WHEN a.type = 'in_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END ) as purchase_amount,
                                  pc.id,pc.name from account_invoice_line as ai
                                       left join account_invoice as a
                                       on a.id=ai.invoice_id
                                       left join product_product as p
                                       on ai.product_id =p.id
                                       left join product_template as pt
                                       on pt.id = p.product_tmpl_id
                                       left join product_category as pc
                                        on (pt.categ_id =pc.id)
                                       where a.type in ('in_invoice','in_refund') and a.state in ('open','paid') and
                                                   pc.id=%s and a.date_invoice BETWEEN %s and %s
                                                   GROUP BY pc.id'''
                self.env.cr.execute(purchase_query, (config_id, date_start, date_end,))
                for row in self.env.cr.dictfetchall():
                    p_qty += row['purchase_qty'] if row['purchase_qty'] else 0
                    p_amt += row['purchase_amount'] if row['purchase_amount'] else 0
                    pf_amt += row['purchase_freeqty'] if row['purchase_freeqty'] else 0
                s = self.env['product.category'].browse(config_id).name
                pname = s

                res = {

                    'pname': pname,

                    'sl_no': sl,
                    'sp_qty': s_qty,
                    'sale_total': s_amt,
                    'p_qty': p_qty + pf_amt,
                    'pur_total': p_amt,
                    'price_unit': price_u,
                    # 'cost': (cost * quantity) if quantity else (cost),
                }

                lines.append(res)


                if res:
                    return res
                else:
                    return []



    # def get_brand(self, data):
    #
    #     lines = []
    #
    #     date_start = data['form']['date_start']
    #     date_end = data['form']['date_end']
    #     # company_id = data['form']['company_id']
    #     category_id = data['form']['category_id']
    #     child_category = data['form']['child_category']
    #     cat_only=data['form']['cat_only']
    #     subcategory_id=data['form']['subcategory_id']
    #
    #
    #
    #     if cat_only==False:
    #
    #
    #
    #         if category_id:
    #             sale_lines = self.env["pos.order.line"].search(
    #                 [('order_id.date_order', '>=', date_start), ('order_id.date_order', '<=', date_end),
    #                   ('product_id.categ_id', '=', category_id),
    #                  ('order_id.state', 'in', ['done', 'paid', 'invoiced'])])
    #
    #             out_invoice_lines = self.env["account.invoice.line"].search(
    #                 [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
    #
    #                  ('invoice_id.type', '=', 'out_invoice'),
    #                  ('product_id.categ_id', '=', category_id),
    #                  ('invoice_id.state', 'in', ['open', 'paid'])])
    #
    #             query1 = '''select * from account_invoice_line as ai
    #                             left join account_invoice as a
    #                             on a.id=ai.invoice_id
    #                             left join product_product as p
    #                             on ai.product_id =p.id
    #                             left join product_template pt
    #                              on (pt.id=p.product_tmpl_id)
    #                             left join product_category as pc
    #                             on (pt.categ_id =pc.id)
    #
    #
    #                             where a.type='in_invoice' and a.state in ('open','paid') and pc.id= %s'''
    #
    #             purchase_lines = self.env["account.invoice.line"].search(
    #                 [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
    #
    #                  ('product_id.categ_id', '=', category_id), ('invoice_id.type', '=', 'in_invoice'),
    #                  ('invoice_id.state', 'in', ['open', 'paid'])])
    #             product = self.env["product.product"].search([('categ_id', '=', category_id)])
    #         else:
    #             sale_lines = self.env["pos.order.line"].search(
    #                 [('order_id.date_order', '>=', date_start), ('order_id.date_order', '<=', date_end),
    #
    #                  ('order_id.state', 'in', ['done', 'paid', 'invoiced'])])
    #             out_invoice_lines = self.env["account.invoice.line"].search(
    #                 [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
    #                  ('invoice_id.type', '=', 'out_invoice'),
    #                  ('invoice_id.state', 'in', ['open', 'paid'])])
    #
    #             purchase_lines_total = self.env["account.invoice.line"].search(
    #                 [
    #                  ('invoice_id.type', '=', 'in_invoice'),
    #                  ('invoice_id.state', 'in', ['open', 'paid'])])
    #
    #             purchase_lines = self.env["account.invoice.line"].search([('invoice_id.type', '=', 'in_invoice'),
    #                                                                       ('invoice_id.date_invoice', '>=', date_start),
    #                                                                       ('invoice_id.date_invoice', '<=', date_end),
    #
    #                                                                       ('invoice_id.state', 'in', ['open', 'paid'])])
    #             product = self.env["product.product"].search([])
    #
    #         for i in product:
    #
    #             sl = 0
    #             pf_amt = 0
    #             s_amt = 0
    #             s_qty = 0
    #             p_qty = 0
    #             p_amt = 0
    #             price_u = 0
    #
    #             cost = 0
    #             gross_profit = 0
    #             gross_profit_per = 0
    #             quantity = 0
    #             landingcost = 0
    #
    #             sl += 1
    #             sale_query = ''' select SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.quantity  ELSE ai.quantity END) as sale_qty,
    #                                SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END) as sale_amount,
    #                                max(ai.price_unit) as price_unit,
    #                                pc.id,pc.name from account_invoice_line as ai
    #                                    left join account_invoice as a
    #                                    on a.id=ai.invoice_id
    #                                    left join product_product as p
    #                                    on ai.product_id =p.id
    #                                    left join product_template as pt
    #                                    on pt.id = p.product_tmpl_id
    #                                    left join product_category as pc
    #                                    on (pt.categ_id =pc.id)
    #
    #                                    where a.type in ('out_invoice','out_refund') and a.state in ('open','paid') and
    #                                    pc.id=%s and a.date_invoice BETWEEN %s and %s
    #                                    GROUP BY pc.id order by sale_qty'''
    #             self.env.cr.execute(sale_query, (child_category, date_start, date_end,))
    #             for row in self.env.cr.dictfetchall():
    #                 s_qty += row['sale_qty'] if row['sale_qty'] else 0
    #                 s_amt += row['sale_amount'] if row['sale_amount'] else 0
    #                 price_u += row['price_unit'] if row['price_unit'] else 0
    #
    #
    #             purchase_query = '''
    #                                select SUM(CASE WHEN a.type = 'in_refund'  then  -1*ai.quantity  ELSE ai.quantity END ) as purchase_qty,
    #                                         SUM(CASE WHEN a.type = 'in_refund'  then  -1*ai.free_qty  ELSE ai.free_qty END ) as purchase_freeqty,
    #                                SUM(CASE WHEN a.type = 'in_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END ) as purchase_amount,
    #                               pc.id,pc.name from account_invoice_line as ai
    #                                    left join account_invoice as a
    #                                    on a.id=ai.invoice_id
    #                                    left join product_product as p
    #                                    on ai.product_id =p.id
    #                                    left join product_template as pt
    #                                    on pt.id = p.product_tmpl_id
    #                                    left join product_category as pc
    #                                     on (pt.categ_id =pc.id)
    #                                    where a.type in ('in_invoice','in_refund') and a.state in ('open','paid') and
    #                                                pc.id=%s and a.date_invoice BETWEEN %s and %s
    #                                                GROUP BY pc.id'''
    #             self.env.cr.execute(purchase_query, (child_category,date_start, date_end,))
    #             for row in self.env.cr.dictfetchall():
    #                 p_qty += row['purchase_qty'] if row['purchase_qty'] else 0
    #                 p_amt += row['purchase_amount'] if row['purchase_amount'] else 0
    #                 pf_amt += row['purchase_freeqty'] if row['purchase_freeqty'] else 0
    #                 # pname = row['name'] if row['name'] else " "
    #
    #
    #
    #
    #
    #             res = {
    #
    #
    #                 'pname': i.categ_id.name,
    #
    #
    #                 'sl_no': sl,
    #                 'sp_qty': s_qty,
    #                 'sale_total': s_amt,
    #                 'p_qty': p_qty + pf_amt,
    #                 'pur_total': p_amt,
    #                 'price_unit': price_u,
    #                 # 'cost': (cost * quantity) if quantity else (cost),
    #             }
    #
    #             lines.append(res)
    #         if lines:
    #             return lines
    #         else:
    #             return []
    #
    #     if cat_only == True:
    #
    #         query21 = '''
    #
    #
    #
    #                              select
    #                                 dd.id as id,dd.pname as pname,
    #                                 dd.salepos_total as salepos_total ,
    #                                 dd.sale_total as sale_total,
    #                                 dd.pur_total as pur_total,
    #                                 dd.purchase_qty as purchase_qty,
    #                                 dd.purchase_freeqty as purchase_freeqty,
    #
    #                                 dd.quantitypos as posquantity,
    #                                 dd.quantitysale as salequantity
    #
    #
    #                                  from
    #                                 (
    #                                 (
    #
    #                         	select pt.categ_id as id ,pc.name as pname, sum (sh.quantity) as onhand,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),2)) as valuation
    #                         	 from stock_history as sh
    #                                  left join product_product as pp on(pp.id=sh.product_id)
    #                                  left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                                  left join product_category pc on (pc.id=pt.categ_id)
    #                                   where  available_in_pos =True
    #                                     group by pt.categ_id,pc.name
    #
    #                                      ) a
    #
    #                                                                 left join
    #                                 (
    #                                 select  pt.categ_id ,sum(aal.price_subtotal_taxinc) as sale_total,sum(quantity) as quantitysale from
    #                                 account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
    #                         	 left join product_product as pp on(pp.id=aal.product_id)
    #                                  left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                                  left join product_category pc on (pc.id=pt.categ_id)
    #
    #                                 where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
    #
    #                                group by  pt.categ_id
    #
    #                                ) b
    #
    #                                                               on a.id=b.categ_id
    #                                                               left join
    #                                 (
    #
    #                                 select  pt.categ_id ,sum(aaal.price_subtotal_taxinc) as pur_total,
    #                                  SUM(aaal.quantity) as purchase_qty,
    #                                                     SUM(aaal.free_qty) as purchase_freeqty from
    #                                 account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    #                         	left join product_product as pp on(pp.id=aaal.product_id)
    #                                  left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                                  left join product_category pc on (pc.id=pt.categ_id)
    #
    #
    #                                 where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
    #
    #                         	group by  pt.categ_id
    #                         	) c
    #                                 on c.categ_id=a.id
    #                                 			left join
    #                                 (
    #                                 select  pt.categ_id  ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
    #                                  from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
    #                                  left join product_product as pp on(pp.id=pol.product_id)
    #                                  left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                                  left join product_category pc on (pc.id=pt.categ_id)
    #                                  where po.invoice_id is NULL and
    #                                  po.state in  ('done', 'paid','invoiced')
    #                                 and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
    #
    #                                  group by  pt.categ_id
    #                                     ) d
    #                                                                 on a.id=d.categ_id
    #                                                                 left join
    #                                                                 (
    #                                                                 select pt.categ_id as categ_id ,sum (sh.quantity) as onhands,
    #                                                                 round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),2)) as salecost1
    #                         	 from stock_history as sh
    #                                  left join product_product as pp on(pp.id=sh.product_id)
    #                                  left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                                  left join product_category pc on (pc.id=pt.categ_id)
    #                                   where  available_in_pos =True
    #                                   and sh.quantity <0
    #                                   and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between %s and %s
    #
    #                                     group by pt.categ_id
    #
    #                                                                 ) f on a.id =f.categ_id
    #
    #                                                                   left join
    #
    #
    #                                                                    (
    #
    #                                select gg.categ_id as categ_id,
    #                     			sum(gg.salecost) as salecost from( select
    #                                 pt.categ_id as categ_id ,
    #                                 aaal.product_id as product_id,
    #
    #                                 sum(aaal.price_subtotal)/nullif (sum(aaal.quantity),0) as salecost from
    #                                 account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    #                             left join product_product as pp on(pp.id=aaal.product_id)
    #                                  left join product_template pt on (pt.id=pp.product_tmpl_id)
    #
    #
    #                                 where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
    #
    #                             group by  aaal.product_id,pt.categ_id)gg group by gg.categ_id
    #                             ) k on a.id=k.categ_id
    #
    #                             left join
    #
    #
    #                                     (   select sum(ss.onhand*yy.salecost) as onhand1,ss.categ_id as categ_id,
    #                                     sum(yy.salecost*(cv.quantitypos)) as totalsalecost1,
    #                                     sum(case when ww.quantitysale is NULL then 0 else ww.quantitysale END)as tt ,
    #                                     sum(case when cv.quantitypos is NULL then 0 else cv.quantitypos END)as qq,
    #
    #                                     sum(yy.salecost) ,
    #                     (sum(yy.salecost*((case when ww.quantitysale is NULL then 0 else ww.quantitysale END)+(case when cv.quantitypos is NULL then 0 else cv.quantitypos END)))) as ttqq,
    #
    #                                     sum(cv.quantitypos+ww.quantitysale) from
    #
    #                                      (select pt.categ_id as categ_id,sh.product_id as id ,pt.name as pname, sum (sh.quantity) as onhand
    #                         			  ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),2)) as valuation
    #                         			  from stock_history as sh
    #                                  left join product_product as pp on(pp.id=sh.product_id)
    #                                  left join product_template pt on (pt.id=pp.product_tmpl_id)
    #
    #                                    group by sh.product_id,pt.name,pt.categ_id
    #                                      )ss
    #                     			left join
    #
    #
    #                     			  ( select
    #                                 pt.categ_id as categ_id ,
    #                                 aaal.product_id as product_id,
    #
    #                                 sum(aaal.price_subtotal)/nullif (sum(aaal.quantity),0) as salecost from
    #                                 account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    #                             left join product_product as pp on(pp.id=aaal.product_id)
    #                                  left join product_template pt on (pt.id=pp.product_tmpl_id)
    #
    #
    #                                 where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
    #
    #                             group by  aaal.product_id,pt.categ_id)yy on ss.id=yy.product_id
    #
    #                             left join
    #
    #                              (
    #                                 select pol.product_id as product_id  ,pt.categ_id as categ_id,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
    #                                  from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
    #                                  left join product_product as pp on(pp.id=pol.product_id)
    #                                  left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                                  where po.invoice_id is NULL and
    #                                  po.state in  ('done', 'paid','invoiced')
    #                                 and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
    #
    #
    #                                  group by pol.product_id,pt.categ_id
    #                                     )cv on ss.id=cv.product_id
    #
    #                                     left join
    #
    #                                     (
    #                                 select aal.product_id as product_id , pt.categ_id as categ_id,sum(aal.price_subtotal_taxinc) as sale_total,sum(quantity) as quantitysale
    #                                  from
    #                                 account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
    #                         	 left join product_product as pp on(pp.id=aal.product_id)
    #                                  left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                                 where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
    #
    #                                group by aal.product_id,pt.categ_id
    #                                ) ww on ww.product_id=ss.id group by ss.categ_id)pk on a.id=pk.categ_id
    #
    #
    #                                left join
    #
    #
    #
    #
    #                         (
    #
    #
    #
    #                         with pos as(
    #                         select
    #
    #                         ddd.product_id ,
    #                         ddd.categ_id,
    #
    #                         ddd.valuation,
    #                         ddd.quantity,
    #                         ddd.avg,
    #                         ddd.quantity*ddd.avg as costofsalewithoutpurchase
    #
    #                          from
    #
    #                         (
    #
    #                         (
    #                         select a.product_id as product_id,
    #
    #                         a.categ_id,
    #                         a.quantity,
    #                         a.valuation
    #                          from (
    #
    #
    #                             select pc.name as psname,max(sh.product_categ_id) as categ_id,max(sh.product_id) as product_id,sum(sh.quantity) as quantity,
    #                             round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),2)) as valuation
    #                                 from stock_history sh left join product_template p on (p.id = sh.product_template_id)
    #                                 left join product_category pc on (pc.id=sh.product_categ_id) where
    #
    #                                   available_in_pos = True  group by sh.product_id,pc.name,sh.product_categ_id order by max(sh.product_id)
    #
    #                                   ) a where  a.quantity <0
    #
    #
    #                         ) aa
    #                         left join
    #
    #
    #
    #                         (
    #
    #                         Select
    #                         COALESCE(product_id ,product_ids )as product_ids,
    #
    #                         (COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) as totalsale,
    #                           (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantity,
    #
    #                         round((COALESCE  ((COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) /   (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) )),2) as avg
    #
    #                          from
    #
    #                           (
    #                                   (
    #                                   select DISTINCT(aal.product_id),sum(aal.price_subtotal_taxinc) as sale_total,sum(quantity) as quantitysale from account_invoice aaa left join
    #                                    account_invoice_line aal  on   (aaa.id=aal.invoice_id)
    #                                      where aaa.type ='out_invoice' and aaa.state in  ('open', 'paid') group by aal.product_id order by   aal.product_id
    #                                      )  a
    #
    #                          full join
    #                                     (
    #                                     select DISTINCT(pol.product_id ) product_ids ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
    #                                  from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
    #                                  left join product_product as pp on(pp.id=pol.product_id)
    #                                  left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                                  left join product_category pc on (pc.id=pt.categ_id)
    #                                  where po.invoice_id is NULL and
    #                                  po.state in  ('done', 'paid','invoiced') group by pol.product_id order by  pol.product_id
    #                                   ) b
    #                                  on a.product_id =b.product_ids  ) dd where
    #                                dd.quantitypos !=0
    #                         ) bb on aa.product_id = bb.product_ids  ) ddd  )
    #                         select categ_id,
    #                         --sum(valuation) as valuation,
    #                         sum(quantity) as quantity,
    #                         sum(avg) as avg,
    #                         sum(costofsalewithoutpurchase) as costofsalewithoutpurchase
    #
    #                          from pos  group by categ_id
    #
    #
    #
    #
    #
    #
    #
    #
    #                         ) h on h.categ_id=a.id
    #
    #
    #
    #
    #
    #                                 ) as dd order by dd.pname
    #
    #
    #
    #
    #
    #
    #
    #
    #                                                                     '''
    #
    #         self.env.cr.execute(query21, (
    #             date_start, date_end,
    #             date_start, date_end,
    #             date_start, date_end,
    #             date_start, date_end,
    #             date_start, date_end,
    #             date_start, date_end,
    #             date_start, date_end,
    #             date_start, date_end,
    #
    #         ))
    #
    #         for row in self.env.cr.dictfetchall():
    #             # sl = sl + 1
    #
    #             sale = 0
    #             possale = 0
    #             purtotal = 0
    #
    #             # poscost = row['poscost'] if row['poscost'] else 0
    #             sale = row['sale_total'] if row['sale_total'] else 0
    #             possale = row['salepos_total'] if row['salepos_total'] else 0
    #             purtotal = row['pur_total'] if row['pur_total'] else 0
    #
    #             totalsale = sale + possale
    #             totalsaleqty = row['salequantity'] if row['salequantity'] else 0
    #             totalposqty = row['posquantity'] if row['posquantity'] else 0
    #
    #             ph_qty = row['purchase_qty'] if row['purchase_qty'] else 0
    #             pf_amt = row['purchase_freeqty'] if row['purchase_freeqty'] else 0
    #             p_qty = ph_qty + pf_amt
    #
    #             res = {
    #
    #
    #                 # 'sl_no': sl,
    #                 'id': row['id'],
    #                 'pname': row['pname'] if row['pname'] else '',
    #                 'sale_total': round(totalsale, 2),
    #                 'pur_total': round(purtotal, 2),
    #
    #                 'sp_qty': round(((totalsaleqty + totalposqty)), 0),
    #                 'p_qty': p_qty
    #
    #             }
    #
    #             lines.append(res)
    #
    #
    #
    #
    #         if lines:
    #             return lines
    #         else:
    #             return []

    @api.model
    def render_html(self, docids, data=None, config_id=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        # company_id = data['form']['company_id']
        category_id = data['form']['category_id']
        child_category = data['form']['child_category']
        cat_only = data['form']['cat_only']
        subcategory_id = data['form']['subcategory_id']
        config = self.env['pos.config'].browse(child_category)
        stock_location = data['form']['stock_location']

        # name_de = self.env['pos.config'].browse(category_id).name


        valueone = 0
        valuefour = 0


        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        rescash = {}
        rescard = {}
        rescashline = []
        rescardline = []
        rescreditline = []
        total_session = []

        if cat_only:
            valueone = self.get_cash(data)

        if not cat_only and child_category:

            for pfg in config:
                cash = self.get_cash_wise(data, pfg.id)

                # total = cash['cash']
                # total_session.append(total)
                rescashline.append(self.get_cash_wise(data, pfg.id))

        valuefour = rescashline


        total_session_wise = total_session


        category_name = self.env["product.category"].browse(category_id).name
        stock_parent = self.env["stock.location"].browse(stock_location).location_id.name
        stock_name = self.env["stock.location"].browse(stock_location).name

        # stock_locationids = stock_parent+'/'+stock_name


        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'date_end': date_object_date_end.strftime('%d-%m-%Y'),
            'category_name': category_name if category_name else 'All Category Report',
            'data': data['form'],
            'time': time,
            # 'name_de':name_de,
            'data': data['form'],
            'doc_ids': self.ids,
            'data': data['form'],
            'doc_ids': self.ids,


            'category_name': category_name,
            'stock_location':stock_name,
            'stock_name':stock_parent,
            # 'location':stock_parent+'/'+stock_name,



            'pos_config_ids':child_category,
            'config': config,
            'time': time,
            'valueone': valueone,

            'cat_only': cat_only,
            'valuefour': valuefour,

            'total_session_wise': total_session_wise,



        }

        return self.env['report'].render('parent_category_pdf.parent_category_pdf', docargs)
