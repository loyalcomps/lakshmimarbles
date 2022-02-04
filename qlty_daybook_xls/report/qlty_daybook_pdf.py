# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Reportdaybook(models.AbstractModel):
    _name = 'report.qlty_daybook_xls.daybook_report_pdf'

    def get_opening(self, data):

        datas = {}
        data2 = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']
        # query1 = '''select default_debit_account_id as account_id from account_journal where  type ='cash' and company_id = %s '''
        # self.env.cr.execute(query1, (branch_ids,))
        # datas = self.env.cr.dictfetchall()
        # accounts = []
        # for a in datas:
        #     accounts.append(a['account_id'])
        # account_ids = tuple(accounts)

        journal = self.env['account.account'].search([('code', '=', '100101')])

        query = '''select sum(l.balance)  FROM account_move_line l left join account_move m on (m.id = l.move_id) WHERE m.date < %s and l.account_id = %s and m.state in ('posted') '''
        # self.env.cr.execute(query, (date_start, tuple(account_ids),))
        self.env.cr.execute(query, (date_start, journal.id))
        data2 = self.env.cr.dictfetchall()
        value = data2[0]['sum']

        if not value:
            value = 0

        return value

    def get_lines_finalpos(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']

        query = '''

           

select dd.dateee as dateee,dd.typess as typess,max(dd.code) as code,max(dd.acname) as acname,

           COALESCE(sum(CASE dd.amount WHEN dd.amount THEN dd.amount ELSE 0 END ),0)  as amount,
           COALESCE(sum(CASE dd.expense WHEN dd.expense THEN dd.expense ELSE 0 END ),0)  as expense
           from (
            select ac.code as code,ac.name as acname,p.name as sname, m.date as dateee,m.ref as bill_no, l.name  as particular  ,l.company_id as comp_id,j.type as typess,
                        round((case
                          when l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
                         then  l.debit
                        else 0 end  ),2) as amount,
                        round((case
                         when l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0 and payment_id is not null
                         then  l.credit
                       when l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0
                        then  l.credit
                        else 0 end  ),2) as expense  ,
                        m.state as state
                        from account_move_line l
                        full join account_account_type t on(t.id=l.user_type_id)
                        full join  account_move m on (m.id=l.move_id)
                        full join account_journal j on (j.id=m.journal_id)
                        left join res_partner p on (p.id =m.partner_id)
                        left join account_account ac on (ac.id=l.account_id)
                        where  m.ref ~* 'POS/' and 
           		    m.date	BETWEEN %s and %s and m.company_id = %s and	    
           		 
                             (  l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
                       or
                       l.user_type_id=(select id from account_account_type where name='Bank and Cash') and payment_id is not null
                       or
                       l.user_type_id=(select id from account_account_type where name='Bank and Cash')
                       or
                       l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0 )
                        )

                       as dd group by dd.dateee,dd.typess order by dd.dateee


                          '''
        self.env.cr.execute(query, (date_start, date_end, branch_ids))
        # sale_amount = 0
        for row in self.env.cr.dictfetchall():
            dates = datetime.strptime(row['dateee'], '%Y-%m-%d').date()
            res = {
                'vname': '',
                'date': dates.strftime('%d-%m-%Y'),
                'sname': 'POS Sale ',

                'particular': row['typess'],
                'code': row['code'] if row['code'] else " ",
                'acname': row['acname'] if row['acname'] else " ",

                'amount': row['amount'],
                'expense': row['expense'],

            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    # def get_lines_finalpos(self, data):
    #     lines = []
    #     res = {}
    #     date_start = data['form']['date_start']
    #     date_end = data['form']['date_end']
    #
    #     branch_ids = data['form']['branch_ids']
    #     query = '''
    #             select dd.jounrnal_id,dd.jname as jname,dd.jtype as jtype,
    #            COALESCE(sum(CASE dd.jounrnal_id WHEN dd.jounrnal_id THEN dd.total ELSE 0 END ),0)  as total
    #            from (
    #                SELECT
    #            pos_order.date_order as odate, pos_order.company_id as company_id,  pos_order.name as oname,
    #              account_bank_statement_line.journal_id as jounrnal_id, account_journal.name as jname,account_journal.type as jtype,
    #             account_bank_statement_line.amount as total FROM
    #              public.pos_order,  public.account_bank_statement_line,  account_journal WHERE
    #          pos_order.id= account_bank_statement_line.pos_statement_id AND
    #          account_journal.id =account_bank_statement_line.journal_id AND
    #         pos_order.state in ('paid','done')
    #            ) as dd  where to_char(date_trunc('day',dd.odate),'YYYY-MM-DD')::date between  %s and %s
    #            and dd.company_id = %s and dd.jtype ='bank'  GROUP BY dd.jounrnal_id,dd.jname,dd.jtype
    #
    #                   '''
    #     self.env.cr.execute(query, (date_start, date_end, branch_ids))
    #     sale_amount = 0
    #     for row in self.env.cr.dictfetchall():
    #
    #
    #
    #         res = {
    #             'sname': 'POS  Sale ',
    #             'type': row['jtype'],
    #             'particular': row['jname'],
    #             'amount': row['total'],
    #         }
    #         lines.append(res)
    #     if lines:
    #         return lines
    #     else:
    #         return []

    def get_lines(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']
        query = '''
                select ac.code as code,ac.name as acname,m.name as vname,p.name as sname, m.date as dateee,m.ref as bill_no,j.type as type, l.name  as particular  ,l.company_id as comp_id,
                 (case
                   when l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
                  then  l.debit
                 else 0 end  ) as amount,
                 (case
                  when l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0 and payment_id is not null
                  then  l.credit
                when l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0  
                 then  l.credit
                 else 0 end  )as expense  ,
                 m.state as state
                 from account_move_line l
                 full join account_account_type t on(t.id=l.user_type_id)
                 full join  account_move m on (m.id=l.move_id)
                 full join account_journal j on (j.id=m.journal_id)
                 left join res_partner p on (p.id =m.partner_id)
                 left join account_account ac on (ac.id=l.account_id)
                 where 
    		 m.date	BETWEEN %s and %s and m.company_id = %s and 
    		  m.ref  is null and   (
                l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
                or
                l.user_type_id=(select id from account_account_type where name='Bank and Cash') and payment_id is not null
                or
                l.user_type_id=(select id from account_account_type where name='Bank and Cash') 
                or
                l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0
                     )
                order by  m.date                
                '''
        self.env.cr.execute(query, (date_start, date_end, branch_ids))

        for row in self.env.cr.dictfetchall():
            dates = datetime.strptime(row['dateee'], '%Y-%m-%d').date()
            res = {
                'vname': row['vname'],
                'date': dates.strftime('%d-%m-%Y'),
                'sname': row['sname'],
                'code': row['code'] if row['code'] else " ",
                'acname': row['acname'] if row['acname'] else " ",
                # 'bill_no': row['bill_no'],
                # 'type': row['type'],
                'particular': row['particular'],
                'amount': row['amount'],
                'expense': row['expense'],
                # 'state': row['state'],
            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    def get_lines_final(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']
        query = '''
                    select ac.code as code,ac.name as acname,m.name as vname,p.name as sname,COALESCE(ap.cheque_reference,'') as cheque, m.date as dateee,m.ref as bill_no,j.type as type, l.name  as particular  ,l.company_id as comp_id,
                     (case
                       when l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
                      then  l.debit
                      when j.type ='bank' 
                      then  l.debit
                     else 0 end  ) as amount,
                     (case
                      when l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0 and payment_id is not null
                      then  l.credit
                    when l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0  
                     then  l.credit
                     else 0 end  )as expense  ,
                     m.state as state
                     from account_move_line l
                     full join account_account_type t on(t.id=l.user_type_id)
                     full join  account_move m on (m.id=l.move_id)
                     full join account_journal j on (j.id=m.journal_id)
                     left join res_partner p on (p.id =m.partner_id)
                     left join account_payment ap on (ap.id = l.payment_id)
                     left join account_account ac on (ac.id=l.account_id)

                     where  COALESCE(m.ref,'/') !~* 'POS' and 
        		    m.date	BETWEEN %s and %s and m.company_id = %s and m.state ='posted' and
                          (
                    l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
                    or
                    l.user_type_id=(select id from account_account_type where name='Bank and Cash') and payment_id is not null
                    or
                    l.user_type_id=(select id from account_account_type where name='Bank and Cash') 
                    or
                    l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0
                         or
                          j.type ='bank' 
                         ) 
                    order by  m.date

                    '''
        self.env.cr.execute(query, (date_start, date_end, branch_ids))
        for row in self.env.cr.dictfetchall():
            dates = datetime.strptime(row['dateee'], '%Y-%m-%d').date()

            particular = str(row['particular'] if row['particular'] else '') + '(' + str(row['cheque']) + ')' if row['cheque'] else ''

            res = {
                'date': dates.strftime('%d-%m-%Y'),
                'sname': row['sname'],
                'vname': row['vname'],
                'code': row['code'] if row['code'] else " ",
                'acname': row['acname'] if row['acname'] else " ",
                # 'bill_no': row['bill_no'],
                # 'type': row['type'],
                'particular': particular,
                'amount': row['amount'],
                'expense': row['expense'],
                'state': row['state'],
            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    def get_lines_saledata(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']

        query = '''select id from pos_order where  state in ('paid','invoiced','done')  
  AND to_char(date_trunc('day',date_order),'YYYY-MM-DD')::date between %s and %s
  AND company_id= %s '''

        self.env.cr.execute(query, (date_start, date_end, branch_ids))
        for row in self.env.cr.dictfetchall():

            lines.append(row['id'])

        if lines:
            st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', lines)]).ids
            if st_line_ids:
                self.env.cr.execute("""
                            SELECT aj.name, sum(amount) total,cast(COALESCE(aj.debt,'false') as char) as debt
                            FROM account_bank_statement_line AS absl,
                                 account_bank_statement AS abs,
                                 account_journal AS aj 
                            WHERE absl.statement_id = abs.id
                                AND abs.journal_id = aj.id 
                                AND absl.id IN %s 
                            GROUP BY aj.name,aj.debt
                        """, (tuple(st_line_ids),))
                payments = self.env.cr.dictfetchall()
            else:
                payments = []
            if payments:
                return payments
            else:
                return []
        else:
            return []





    def get_lines_taxin(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']
        query = '''
        Select COALESCE(dd.t_name,'GST 0') as tname,
    COALESCE(sum(dd.tax_amount),0)  as tamount
    from (
      SELECT avt.invoice_id as invoice_id,j.date_invoice as date_invoice,
        j.reference as sreference,
        j.number as inv_no,
        round(j.amount_total,2) as amount_total,
        round(j.amount_untaxed,2) as amount_untaxed,
        round(j.amount_tax,2) as amount_tax,
        round(j.amount_discount,2) as amount_discount,
        p.name as ppname,
        p.street as ppaddress,
        avt.name,
        tax.amount as t_amount,
        tax.cess as cess,
        tax.name as t_name,
        round(avt.amount,2) tax_amount,
        --p.gst_in as gstin
        p.x_gstin as gstin
        from account_invoice as j left join 
        account_invoice_tax as avt on ( j.id=avt.invoice_id) left join 
        res_partner as p on (p.id=j.partner_id)
        left join account_tax as tax on (tax.id=avt.tax_id)
        where 
        j.date_invoice BETWEEN %s and %s   and j.company_id = %s and 
        j.state in ('open','paid')  and j.type='in_invoice'  
         -- and p.gst_in is not null  
        order by j.date_invoice



        ) as dd 
        
        group by dd.t_name '''

        self.env.cr.execute(query, (date_start, date_end, branch_ids))
        for row in self.env.cr.dictfetchall():
            res = {
                'name': row['tname'],
                'amount': row['tamount']
            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    def get_lines_taxout(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']
        query = '''
               Select
 
 	COALESCE(dd.t_name,'GST 0') as tname,
    COALESCE(sum(dd.tax_amount),0)  as tamount
    from (
      SELECT avt.invoice_id as invoice_id,j.date_invoice as date_invoice,
        j.reference as sreference,
        j.number as inv_no,
        round(j.amount_total,2) as amount_total,
        round(j.amount_untaxed,2) as amount_untaxed,
        round(j.amount_tax,2) as amount_tax,
        round(j.amount_discount,2) as amount_discount,
        p.name as ppname,
        p.street as ppaddress,
        avt.name,
        tax.amount as t_amount,
        tax.cess as cess,
        tax.name as t_name,
        round(avt.amount,2) tax_amount,
        --p.gst_in as gstin
        p.x_gstin as gstin
        from account_invoice as j left join 
        account_invoice_tax as avt on ( j.id=avt.invoice_id) left join 
        res_partner as p on (p.id=j.partner_id)
        left join account_tax as tax on (tax.id=avt.tax_id)
        where 
        j.date_invoice BETWEEN %s and %s   and j.company_id = %s and 
        j.state in ('open','paid')  and j.type='out_invoice'  
         -- and p.gst_in is not null  
        order by j.date_invoice



        ) as dd 
        
        group by dd.t_name
        
        
UNION

SELECT  

dd.tname as tname,
COALESCE(sum( dd.taxamount  ),0)  as tamount

 from
(

SELECT 
  pos_order.id as posid, 
  pos_order.date_order as odate,
  COALESCE(account_tax.name,'GST 0') as tname,
   COALESCE(account_tax.amount,'0')  as tamount, 
    account_tax.cess as cess,
  pos_order.name as oname, 
  round(sum((pos_order_line.qty * pos_order_line.price_unit) - pos_order_line.discount),2) as total,
  round(sum((pos_order_line.qty * pos_order_line.price_unit) - pos_order_line.discount) * (COALESCE(account_tax.amount,'0')/(100+COALESCE(account_tax.amount,'0'))),2) as taxamount, 
  round(sum((pos_order_line.qty * pos_order_line.price_unit) - pos_order_line.discount) * 100 / (100+COALESCE(account_tax.amount,'0')),2)  as untaxamount
FROM 
  public.pos_order 
  left join public.pos_order_line   on (pos_order.id = pos_order_line.order_id)
  left join public.account_tax_pos_order_line_rel on (pos_order_line.id = account_tax_pos_order_line_rel.pos_order_line_id)
  left join public.account_tax  on (account_tax_pos_order_line_rel.account_tax_id = account_tax.id )
WHERE 
  pos_order.state in ('paid','done')  
  AND to_char(date_trunc('day',pos_order.date_order),'YYYY-MM-DD')::date between %s and %s
  AND pos_order_line.company_id= %s

   group by account_tax.name ,pos_order.id,pos_order_line.qty,pos_order_line.discount,
  account_tax.amount,pos_order_line.price_unit,account_tax.cess 
  
   ) as dd 
   group by dd.tname 
  
                    '''
        self.env.cr.execute(query, (date_start, date_end, branch_ids, date_start, date_end, branch_ids))
        for row in self.env.cr.dictfetchall():
            res = {
                'name': row['tname'],
                'amount': row['tamount']
            }
            lines.append(res)
        if lines:
            # taxlist =[]
            taxdist = {}
            linelist = []

            for io in lines:

                if io['name'] in taxdist:
                    taxdist[io['name']] += io['amount']
                else:
                    taxdist[io['name']] = io['amount']
            # taxlist.append(taxdist)
            for k, l in taxdist.iteritems():
                linedist = {}

                # print k
                # print l
                linedist['name'] = k
                linedist['amount'] = round(l, 2)

                linelist.append(linedist)

            return linelist
        else:
            return []

    @api.model
    def render_html(self, docids, data=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        detailed = data['form']['detailed']
        opening_bal = self.get_opening(data)

        valuesfive = 0.0
        valuesfour = 0.0
        valuesone = 0.0
        valuessix = 0.0
        valuestwo = 0.0

        if detailed:
            valuestwo = self.get_lines_saledata(data)
            valuesfive = self.get_lines_taxout(data)
            valuessix = self.get_lines_taxin(data)

        valuesone = self.get_lines_finalpos(data)

        # valuesthree = self.get_lines(data)
        valuesfour = self.get_lines_final(data)

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'date_end': date_object_date_end.strftime('%d-%m-%Y'),
            'data': data['form'],
            'time': time,
            'detailed':detailed,
            'valuesone': valuesone,
            'valuestwo':valuestwo,
            # 'valuesthree':valuesthree,
            'valuesfour': valuesfour,
            'valuesfive': valuesfive,
            'valuessix': valuessix,
            'opening_bal': opening_bal,

        }

        return self.env['report'].render('qlty_daybook_xls.daybook_report_pdf', docargs)
