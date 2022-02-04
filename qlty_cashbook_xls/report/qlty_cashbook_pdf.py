# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Reportcashbook(models.AbstractModel):

    _name = 'report.qlty_cashbook_xls.cashbook_report_pdf'

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

        journal_ids = data['form']['journal_ids']
        journal = self.env['account.journal'].browse(data['form']['journal_ids']).default_debit_account_id

        query = '''select sum(l.balance)  FROM account_move_line l left join account_move m on (m.id = l.move_id) WHERE m.date < %s and l.account_id = %s and m.state in ('posted') '''
        # self.env.cr.execute(query, (date_start, tuple(account_ids),))
        self.env.cr.execute(query, (date_start,journal.id))
        data2 = self.env.cr.dictfetchall()
        value = data2[0]['sum']

        if not value:
            value = 0

        return value

    def get_lines_final(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        journal_ids = data['form']['journal_ids']
        journal = self.env['account.journal'].browse(data['form']['journal_ids']).default_debit_account_id
        branch_ids = data['form']['branch_ids']
        query = '''
                    select m.name as vname,p.name as sname, m.date as dateee,m.ref as bill_no,j.type as type, l.name  as particular  ,l.company_id as comp_id,
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
                     where  COALESCE(m.ref,'/') !~* 'POS' and m.state ='posted' and
        		    m.date	BETWEEN %s and %s and m.company_id = %s and	    
        		     l.account_id = %s and
                          (  l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
                    or
                    l.user_type_id=(select id from account_account_type where name='Bank and Cash') and payment_id is not null
                    or
                    l.user_type_id=(select id from account_account_type where name='Bank and Cash')
                    or
                    l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0 )
                    order by m.date

                    '''
        self.env.cr.execute(query, (date_start, date_end, branch_ids,journal.id))
        for row in self.env.cr.dictfetchall():
            dates = datetime.strptime(row['dateee'], '%Y-%m-%d').date()

            res = {
                'vname' : row['vname'],
                'date': dates.strftime('%d-%m-%Y'),
                'particular': str(row['sname']) if row['sname'] else '/' + '' + str(row['particular']) if row['particular'] else '/' + '' + str(row['bill_no']) if row['bill_no'] else '/',
                'amount': row['amount'],
                'expense': row['expense'],

            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    def get_lines_finalpos(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']
        journal_ids = data['form']['journal_ids']
        journal = self.env['account.journal'].browse(data['form']['journal_ids']).default_debit_account_id

        query = '''

          select dd.dateee as dateee,

          COALESCE(sum(CASE dd.amount WHEN dd.amount THEN dd.amount ELSE 0 END ),0)  as amount,
          COALESCE(sum(CASE dd.expense WHEN dd.expense THEN dd.expense ELSE 0 END ),0)  as expense
          from (
           select p.name as sname, m.date as dateee,m.ref as bill_no, l.name  as particular  ,l.company_id as comp_id,
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
                       where  m.ref ~* 'POS/' and 
          		    m.date	BETWEEN %s and %s and m.company_id = %s and	    
          		     l.account_id = %s and
          		     j.id =%s and
                            (  l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
                      or
                      l.user_type_id=(select id from account_account_type where name='Bank and Cash') and payment_id is not null
                      or
                      l.user_type_id=(select id from account_account_type where name='Bank and Cash')
                      or
                      l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0 )
                       )

                      as dd group by dd.dateee order by dd.dateee


                         '''
        self.env.cr.execute(query, (date_start, date_end, branch_ids, journal.id, journal_ids))
        for row in self.env.cr.dictfetchall():
            dates = datetime.strptime(row['dateee'], '%Y-%m-%d').date()
            res = {
                'vname' : '',
                'date': dates.strftime('%d-%m-%Y'),
                'particular': ' POS Sale',
                'amount': row['amount'],
                'expense': row['expense'],

            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []


    def get_lines(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        journal_ids = data['form']['journal_ids']
        journal = self.env['account.journal'].browse(data['form']['journal_ids']).default_debit_account_id
        branch_ids = data['form']['branch_ids']

        query = '''       
                   select m.name as vname, p.name as sname, m.date as dateee,m.ref as bill_no,j.type as type, l.name  as particular  ,l.company_id as comp_id,
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
                    where
       		     m.date	BETWEEN %s and %s and m.company_id = %s and	 l.account_id= %s and
       		     m.ref  is null and   (
                   l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
                   or
                   l.user_type_id=(select id from account_account_type where name='Bank and Cash') and payment_id is not null
                   or
                   l.user_type_id=(select id from account_account_type where name='Bank and Cash')
                   or
                   l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0
                        )
                   order by m.date                             
                   '''
        self.env.cr.execute(query, (date_start, date_end, branch_ids, journal.id))
        for row in self.env.cr.dictfetchall():
            dates = datetime.strptime(row['dateee'], '%Y-%m-%d').date()

            res = {
                'vname' : row['vname'],
                'date': dates.strftime('%d-%m-%Y'),
                'particular': row['sname'] if row['sname'] else '/' + '' + row['particular'] if row['particular'] else '/',
                'amount': row['amount'],
                'expense': row['expense'],
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
        journal_ids = data['form']['journal_ids']
        journal = self.env['account.journal'].browse(data['form']['journal_ids']).default_debit_account_id
        branch_ids = data['form']['branch_ids']
        journal_name = self.env['account.journal'].browse(data['form']['journal_ids']).name
        opening_bal = self.get_opening(data)
        valuesone = self.get_lines_finalpos(data)
        # valuestwo = self.get_lines(data)
        valuesthree = self.get_lines_final(data)
        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'doc_ids': self.ids,
            'date_start':date_object_date_start.strftime('%d-%m-%Y'),
            'date_end':date_object_date_end.strftime('%d-%m-%Y'),
            'journal_name': journal_name,
            'data': data['form'],
            'time': time,
            'valuesone': valuesone,
            # 'valuestwo':valuestwo,
            'valuesthree':valuesthree,
            'opening_bal':opening_bal,

        }

        return self.env['report'].render('qlty_cashbook_xls.cashbook_report_pdf', docargs)
