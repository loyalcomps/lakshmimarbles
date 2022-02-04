from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime
from odoo import models,fields,api,_


class qltybankbookpdf(models.AbstractModel):
    _name = 'report.qlty_bankbook_xls.bankbook_report_pdf'

    def get_opening(self, data):

        datas = {}
        data2 = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']
        bank_id = data['form']['bank_id']
        query1 = '''select default_debit_account_id as account_id from account_journal where type='bank' and company_id = %s and id=%s '''
        self.env.cr.execute(query1, (branch_ids, bank_id))
        datas = self.env.cr.dictfetchall()
        accounts = []
        for a in datas:
            accounts.append(a['account_id'])
        account_ids = tuple(accounts)
        query = '''select sum(balance)  FROM account_move_line WHERE date < %s and account_id in %s '''
        self.env.cr.execute(query, (date_start, tuple(account_ids),))
        data2 = self.env.cr.dictfetchall()
        value = data2[0]['sum']

        if not value:
            value = 0

        return value

    def get_lines(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        journal_ids = data['form']['bank_id']
        journal = self.env['account.journal'].browse(data['form']['bank_id']).default_debit_account_id
        branch_ids = data['form']['branch_ids']

        query = '''       
                select p.name as sname, m.date as dateee,m.ref as bill_no,j.type as type, l.name  as particular  ,l.company_id as comp_id,
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
                'date': dates.strftime('%d-%m-%Y'),
                'sname': row['sname'],
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
        journal_ids = data['form']['bank_id']
        journal = self.env['account.journal'].browse(data['form']['bank_id']).default_debit_account_id
        branch_ids = data['form']['branch_ids']
        query = '''
                    select p.name as sname, m.date as dateee,m.ref as bill_no,j.type as type, l.name  as particular  ,l.company_id as comp_id,
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
                     where  m.ref !~* 'POS' and 
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
        self.env.cr.execute(query, (date_start, date_end, branch_ids, journal.id))
        for row in self.env.cr.dictfetchall():
            dates = datetime.strptime(row['dateee'], '%Y-%m-%d').date()

            res = {
                'date': dates.strftime('%d-%m-%Y'),
                'sname': row['sname'],
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

    def get_lines_finalpos(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']
        journal_ids = data['form']['bank_id']
        journal = self.env['account.journal'].browse(data['form']['bank_id']).default_debit_account_id

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
        self.env.cr.execute(query, (date_start, date_end, branch_ids, journal.id))
        # sale_amount = 0
        for row in self.env.cr.dictfetchall():
            # sale_amount += row['total']
            # pos_amount = row['pos_sale_amount'] if row['pos_sale_amount'] else 0.00
            # res = {
            #     'sl_no': sl,
            #     'category': row['category_name'],
            #     'sale': sale_amount + pos_amount,

            res = {
                'date': row['dateee'],
                'sname': 'POS Sale ',
                # 'bill_no': row['bill_no'],
                # 'type': row['jtype'],
                # 'particular': row['jname'],
                'amount': row['amount'],
                # 'total' : sale_amount,
                'expense': row['expense'],
                # 'state': row['state'],
            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []



    @api.model
    def render_html(self, docids, data=None, ):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        get_opening = self.get_opening(data)
        get_lines = self.get_lines(data)
        get_lines_final = self.get_lines_final(data)
        get_lines_finalpos = self.get_lines_finalpos(data)
        journal = self.env['account.journal'].browse(data['form']['bank_id']).name



        date_object_startdate = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_enddate = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'journal':journal,
            'doc_ids': self.ids,
            'date_start': date_object_startdate.strftime('%d-%m-%Y'),
            'date_end': date_object_enddate.strftime('%d-%m-%Y'),
            'data': data['form'],
            'get_opening': get_opening,
            'get_lines': get_lines,
            'get_lines_final':get_lines_final,
            'get_lines_finalpos':get_lines_finalpos,
        }

        return self.env['report'].render('qlty_bankbook_xls.bankbook_report_pdf', docargs)



