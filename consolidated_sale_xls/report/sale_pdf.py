from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime

from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime
from odoo import models,fields,api,_


class consolidatedsalepdf(models.AbstractModel):
    _name = 'report.consolidated_sale_xls.sale_report_pdf'

    def get_opening(self, data):

        datas = {}
        data2 = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        query1 = '''select default_debit_account_id as account_id from account_journal where  type ='cash' and company_id = %s '''
        self.env.cr.execute(query1, (company_id,))
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

    def get_total_sale(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        sl = 0

        query = '''

                     select 
                                COALESCE(sum(CASE dd.jtype WHEN dd.jtype THEN dd.pos_sale_amount ELSE 0 END ),0)  as total,
                                COALESCE(sum(CASE dd.jtype WHEN 'cash' THEN dd.pos_sale_amount ELSE 0 END ),0)  as cashtotal,
                                COALESCE(sum(CASE dd.jtype WHEN 'bank' THEN dd.pos_sale_amount ELSE 0 END ),0)  as cardtotal
                                from (
                                select pos.name as pname,abs.amount pos_sale_amount,po.name as oname,aj.type as jtype,
                                CAST(pos.start_at AS DATE) as start_at from
                                       account_bank_statement_line as abs
                                        left join pos_order as po on po.id=abs.pos_statement_id
                                        left join account_journal as aj  on aj.id=abs.journal_id
                                        left join pos_session as pos on pos.id=po.session_id
                                        where  po.state in ('done','paid','invoiced') and
            				po.company_id = %s
            				and CAST(pos.start_at AS DATE) between %s and %s

                                        GROUP BY CAST(pos.start_at AS DATE),abs.amount,po.name,aj.type ,pos.name
                                        ) as dd
                                        '''

        # #
        # qu
        #
        #
        #
        # ery = '''
        #
        #      select sum(sale_amount) as samount,sum(pos_sale_amount) as posamount
        #             from (
        #                 select  sale_amount, COALESCE(sale_date) AS ssale_date from
        #
        #                 (select SUM(a.amount_total) as sale_amount,a.date_invoice as sale_date from account_invoice as a
        #                     where a.type='out_invoice' and a.state in ('open','paid') and
        #                     a.company_id = %s and a.date_invoice BETWEEN %s and %s
        #                     GROUP BY a.date_invoice) bb
        #                     ) aaa
        #             full join
        #
        #                 (select SUM(round(((pol.qty * pol.price_unit) - pol.discount),2) ) as pos_sale_amount,CAST(po.date_order AS DATE) as pos_date from pos_order_line as pol
        #                     left join pos_order as po
        #                     on po.id=pol.order_id
        #                     where  po.state in ('done','paid') and
        #                     po.company_id = %s and CAST(po.date_order AS DATE) BETWEEN %s and %s
        #                     GROUP BY CAST(po.date_order AS DATE)) cc
        #                     on aaa.ssale_date =cc.pos_date
        #
        #
        #
        #                    '''

        self.env.cr.execute(query, (company_id, date_start, date_end,

                                    ))
        for row in self.env.cr.dictfetchall():
            sl += 1

            # dates = datetime.strptime(row['sale_date'], '%Y-%m-%d').date()

            res = {
                'total': row['total'] if row['total'] else 0,
                'cash': row['cashtotal'] if row['cashtotal'] else 0,
                'card': row['cardtotal'] if row['cardtotal'] else 0

            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_put_money(self, data, config_id):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        sl = 0


        query = '''




     SELECT  
                            sum(dd.amount) as amount

                     from
                    (




                    SELECT 
                      pos_session.id as posid, 
                      pos_session.start_at as odate,
                      pos_session.config_id as conid,
                      account_bank_statement_line.amount as amount

                    from
                      public.pos_session, 
                      public.account_bank_statement_line, 
                      public.pos_config_journal_rel,
                      public.res_company



                    where 
    		  pos_config_journal_rel.pos_config_id = pos_session.config_id AND
    		  pos_config_journal_rel.journal_id = pos_session.cash_journal_id AND
    		  account_bank_statement_line.statement_id = pos_session.cash_register_id  AND
    		  account_bank_statement_line.pos_statement_id is NULL AND
    		  res_company.transfer_account_id = account_bank_statement_line.account_id AND
    		   account_bank_statement_line.amount > 0



                      AND to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s AND pos_session.config_id = %s
    			and account_bank_statement_line.company_id=%s




                       group by account_bank_statement_line.amount ,pos_session.id,pos_session.config_id

                       ) as dd
                               '''
        self.env.cr.execute(query, (date_start, date_end, config_id, company_id))
        for row in self.env.cr.dictfetchall():
            sl += 1
            # put_money_in = row['amount'] if row['amount'] else 0

            # dates = datetime.strptime(row['pdate'], '%Y-%m-%d').date()

            res = {

                'put_money_in': row['amount'] if row['amount'] else 0,

            }

            # lines.append(res)
            if res:
                return res
            else:
                return []

    def get_totalputmoney(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        sl = 0

        query = '''


                                               SELECT  
                                    sum(dd.amount) as amount

                             from
                            (




                            SELECT 
                              pos_session.id as posid, 
                              account_bank_statement_line.amount as amount

                            from
                              public.pos_session, 
                              public.account_bank_statement_line, 
                              public.pos_config_journal_rel,
                              public.res_company


                            where 
            		  pos_config_journal_rel.pos_config_id = pos_session.config_id AND
            		  pos_config_journal_rel.journal_id = pos_session.cash_journal_id AND
            		  account_bank_statement_line.statement_id = pos_session.cash_register_id  AND
            		  account_bank_statement_line.pos_statement_id is NULL AND
            		  res_company.transfer_account_id = account_bank_statement_line.account_id AND

            		  account_bank_statement_line.amount > 0



                              AND to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s
    				and account_bank_statement_line.company_id=%s




                               group by account_bank_statement_line.amount ,pos_session.id

                               ) as dd
                                                   '''
        self.env.cr.execute(query, (date_start, date_end, company_id,
                                    ))
        for row in self.env.cr.dictfetchall():
            sl += 1
            put_money_in = row['amount'] if row['amount'] else 0

            # dates = datetime.strptime(row['pdate'], '%Y-%m-%d').date()

            res = {

                'put_money_in': put_money_in,

            }

            lines.append(res)
        if lines:
            return lines
        else:
            return []

    def get_take_money(self, data, config_id):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        sl = 0


        query = '''



                                SELECT  
                            sum(dd.amount) as amount

                     from
                    (




                    SELECT 
                      pos_session.id as posid, 
                      pos_session.start_at as odate,
                      pos_session.config_id as conid,
                      account_bank_statement_line.amount as amount

                    from
                      public.pos_session, 
                      public.account_bank_statement_line, 
                      public.pos_config_journal_rel,
                      public.res_company



                    where 
    		  pos_config_journal_rel.pos_config_id = pos_session.config_id AND
    		  pos_config_journal_rel.journal_id = pos_session.cash_journal_id AND
    		  account_bank_statement_line.statement_id = pos_session.cash_register_id  AND
    		  account_bank_statement_line.pos_statement_id is NULL AND
    		  res_company.transfer_account_id = account_bank_statement_line.account_id AND

    		  account_bank_statement_line.amount < 0







                      AND to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s AND pos_session.config_id = %s
    	          and account_bank_statement_line.company_id=%s




                       group by account_bank_statement_line.amount ,pos_session.id,pos_session.config_id

                       ) as dd


                               '''
        self.env.cr.execute(query, (date_start, date_end, config_id, company_id))
        for row in self.env.cr.dictfetchall():
            sl += 1

            res = {

                'take_money': row['amount'] if row['amount'] else 0,

            }

            # lines.append(res)

            if res:
                return res
            else:
                return []

    def get_total_takemoney(self, data):

        lines = []
        res = {}

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        query = '''

       SELECT  
                                    sum(dd.amount) as amount

                             from
                            (




                            SELECT 
                              pos_session.id as posid, 
                              account_bank_statement_line.amount as amount

                            from
                              public.pos_session, 
                              public.account_bank_statement_line, 
                              public.pos_config_journal_rel,
                              public.res_company


                            where 
            		  pos_config_journal_rel.pos_config_id = pos_session.config_id AND
            		  pos_config_journal_rel.journal_id = pos_session.cash_journal_id AND
            		  account_bank_statement_line.statement_id = pos_session.cash_register_id  AND
            		  account_bank_statement_line.pos_statement_id is NULL AND
            		  res_company.transfer_account_id = account_bank_statement_line.account_id AND
            		  account_bank_statement_line.amount < 0



                              AND to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s and 
                              account_bank_statement_line.company_id=%s





                               group by account_bank_statement_line.amount ,pos_session.id

                               ) as dd
                                                   '''
        self.env.cr.execute(query, (date_start, date_end, company_id,
                                    ))
        for row in self.env.cr.dictfetchall():
            take_money = row['amount'] if row['amount'] else 0

            # dates = datetime.strptime(row['pdate'], '%Y-%m-%d').date()

            res = {

                'take_money': take_money,

            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_saletotal(self, data, config_id):
        lines = []
        res = {}

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        sl = 0

        query = '''

                        select dd.pname as pname,dd.start_at pos_date,
                                COALESCE(sum(CASE dd.jtype WHEN dd.jtype THEN dd.pos_sale_amount ELSE 0 END ),0)  as total,
                                COALESCE(sum(CASE dd.jtype WHEN 'cash' THEN dd.pos_sale_amount ELSE 0 END ),0)  as cashtotal,
                                COALESCE(sum(CASE dd.jtype WHEN 'bank' THEN dd.pos_sale_amount ELSE 0 END ),0)  as cardtotal
                                from (
                                select pos.name as pname,abs.amount pos_sale_amount,po.name as oname,aj.type as jtype,
                                CAST(pos.start_at AS DATE) as start_at from 
                                       account_bank_statement_line as abs
                                        left join pos_order as po on po.id=abs.pos_statement_id
                                        left join account_journal as aj  on aj.id=abs.journal_id 
                                        left join pos_session as pos on pos.id=po.session_id
                                        where  po.state in ('done','paid') and

            				po.company_id = %s
            				and CAST(pos.start_at AS DATE) between %s and %s
                                        and pos.config_id = %s
                                        GROUP BY CAST(pos.start_at AS DATE),abs.amount,po.name,aj.type ,pos.name
                                        ) as dd 
                                        GROUP BY dd.start_at,dd.pname order by dd.start_at,dd.pname


                                               '''

        self.env.cr.execute(query, (company_id, date_start, date_end, config_id,

                                    ))
        for row in self.env.cr.dictfetchall():

            sl += 1

            stotal = row['total'] if row['total'] else 0

            # dates = datetime.strptime(row['sale_date'], '%Y-%m-%d').date()

            res = {
                'total': stotal,

            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_startbal(self, data, config_id):
        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']



        sl = 0

        query = '''

                                   SELECT  
                            sum(dd.amount) as amount

                     from
                    (
                    SELECT 
                      pos_session.id as posid, 
                      pos_session.config_id as conid,

                      account_bank_statement.balance_start as amount

                    from
                      public.pos_session, 
                      public.account_bank_statement,
                      public.account_bank_statement_cashbox



                    where 
    account_bank_statement.pos_session_id = pos_session.id AND
    pos_session.cash_register_id = account_bank_statement.id AND
            account_bank_statement.cashbox_start_id = account_bank_statement_cashbox.id




     AND to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s

     AND pos_session.config_id = %s and account_bank_statement.company_id=%s





                       group by account_bank_statement.balance_start ,pos_session.id,pos_session.config_id

                       ) as dd 
                                               '''

        self.env.cr.execute(query, (date_start, date_end, config_id, company_id))
        for row in self.env.cr.dictfetchall():
            sl += 1

            res = {

                'openbalance': row['amount'] if row['amount'] else 0,

            }
            # lines.append(res)
            if res:
                return res
            else:
                return []

    def get_totstartbal(self, data):

        lines = []
        res = {}

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        sl = 0

        query = '''

                         SELECT  
                                    sum(dd.amount) as amount

                             from
                            (
                            SELECT 
                              pos_session.id as posid, 
                              account_bank_statement.balance_start as amount


                            from
                              public.pos_session, 
                              public.account_bank_statement,
                              public.account_bank_statement_cashbox



                            where 
            account_bank_statement.pos_session_id = pos_session.id AND
            pos_session.cash_register_id = account_bank_statement.id AND
                    account_bank_statement.cashbox_start_id = account_bank_statement_cashbox.id




             AND to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s
             and account_bank_statement.company_id=%s






                               group by account_bank_statement.balance_start ,pos_session.id

                               ) as dd 

                                            '''

        self.env.cr.execute(query, (date_start, date_end, company_id))
        for row in self.env.cr.dictfetchall():
            sl += 1

            res = {

                'openbalance': row['amount'] if row['amount'] else 0,

            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    def get_endbal(self, data, config_id):
        lines = []
        # res = {}

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']



        sl = 0

        query = '''

                    SELECT  
                                sum(dd.amount) as amount

                         from
                        (
                        SELECT 
                          pos_session.id as posid, 
                          pos_session.config_id as conid,

                          account_bank_statement.balance_end as amount

                        from
                          public.pos_session, 
                          public.account_bank_statement,
                          public.account_bank_statement_cashbox



                        where 
        account_bank_statement.pos_session_id = pos_session.id AND
        pos_session.cash_register_id = account_bank_statement.id AND
        account_bank_statement.cashbox_start_id = account_bank_statement_cashbox.id




         AND to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s AND pos_session.config_id = %s
         and account_bank_statement.company_id=%s





                           group by account_bank_statement.balance_end ,pos_session.id,pos_session.config_id

                           ) as dd

                                                   '''

        self.env.cr.execute(query, (date_start, date_end, config_id, company_id))
        for row in self.env.cr.dictfetchall():
            sl += 1

            res = {

                'endbalance': row['amount'] if row['amount'] else 0,

            }
            # lines.append(res)

            if res:
                return res
            else:
                return []

    def get_totalendbal(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        sl = 0

        query = '''
      SELECT  
                                    sum(dd.amount) as amount

                             from
                            (
                            SELECT 
                              pos_session.id as posid, 
                              account_bank_statement.balance_end as amount

                            from
                              public.pos_session, 
                              public.account_bank_statement,
                              public.account_bank_statement_cashbox



                            where 
            account_bank_statement.pos_session_id = pos_session.id AND
            pos_session.cash_register_id = account_bank_statement.id AND
            account_bank_statement.cashbox_start_id = account_bank_statement_cashbox.id




             AND to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s
             and account_bank_statement.company_id=%s





                               group by account_bank_statement.balance_end ,pos_session.id

                               ) as dd
                                                '''

        self.env.cr.execute(query, (date_start, date_end, company_id))
        for row in self.env.cr.dictfetchall():
            sl += 1

            res = {

                'endbalance': row['amount'] if row['amount'] else 0,

            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    def get_debtcard(self, data, config_id):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        sl = 0

        query = '''
     SELECT  
                                    sum(dd.balance) as amount

                             from
                            (

    		SELECT

                        -st_line.amount as balance,
                        session.config_id as con_id



                    FROM account_bank_statement_line as st_line
                        LEFT JOIN account_bank_statement st ON (st.id=st_line.statement_id)
                        LEFT JOIN account_journal journal ON (journal.id=st.journal_id)
                        LEFT JOIN pos_order o ON (o.id=st_line.pos_statement_id)

                        LEFT JOIN pos_session session ON (session.id=o.session_id)
                    WHERE
                        journal.debt=true
                        and  -st_line.amount<0

                         AND to_char(date_trunc('day',st_line.date),'YYYY-MM-DD')::date between %s and %s and session.config_id = %s
    				and st_line.company_id=%s




                               group by st_line.amount ,session.id,session.config_id

                               ) as dd

                                                '''

        self.env.cr.execute(query, (date_start, date_end, config_id, company_id))
        for row in self.env.cr.dictfetchall():
            sl += 1

            res = {

                'debtamount': row['amount'] if row['amount'] else 0,

            }
            # lines.append(res)
            if res:
                return res
            else:
                return []

    def get_cash(self, data):
        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        if counter_only:
            cash = 0
            sessions_ids = self.env['pos.session'].search([

                ('config_id', 'in', pos_config_ids)])
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done']),
                                                      ('session_id', 'in', sessions_ids.ids)])

            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])
                for account in pos_account:
                    if account.journal_id.type == 'cash' and account.journal_id.debt == False:
                        cash += account.amount

        else:

            cash = 0
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done'])])
            account_invoice = self.env['account.invoice'].search(
                [('date_invoice', '>=', date_start), ('date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('state', 'in', ['paid', 'open']), ('type', '=', 'out_invoice')])
            for invoice in account_invoice:
                for i in invoice.payment_move_line_ids:
                    account_move_line = self.env['account.move.line'].search(
                        [('id', '=', i.id), ('journal_id.type', '=', 'cash'), ('journal_id.debt', '=', False),
                         ('move_id.state', '=', 'posted')])
                    for j in account_move_line:
                        cash += j.credit

            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])
                for account in pos_account:
                    if account.journal_id.type == 'cash' and account.journal_id.debt == False:
                        cash += account.amount

        res = {
            'cash': cash,
        }

        lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_card(self, data):

        lines = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        if counter_only:
            card = 0
            sessions_ids = self.env['pos.session'].search([

                ('config_id', 'in', pos_config_ids)])
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done']),
                                                      ('session_id', 'in', sessions_ids.ids)])

            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])
                for account in pos_account:
                    if account.journal_id.type == 'bank':
                        card += account.amount

        else:

            card = 0
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done'])])
            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])
                for account in pos_account:
                    if account.journal_id.type == 'bank':
                        card += account.amount
            account_invoice = self.env['account.invoice'].search(
                [('date_invoice', '>=', date_start), ('date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('state', 'in', ['paid', 'open']), ('type', '=', 'out_invoice')])
            for invoice in account_invoice:
                for i in invoice.payment_move_line_ids:
                    account_move_line = self.env['account.move.line'].search(
                        [('id', '=', i.id), ('journal_id.type', '=', 'bank'), ('move_id.state', '=', 'posted')])
                    for j in account_move_line:
                        card += j.credit
        res = {
            'card': card,
        }

        lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_credit(self, data):

        lines = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        sl = 0

        query = '''

     SELECT  
                                    sum(dd.balance) as amount

                             from
                            (

    		SELECT

                        -st_line.amount as balance




                    FROM account_bank_statement_line as st_line
                        LEFT JOIN account_bank_statement st ON (st.id=st_line.statement_id)
                        LEFT JOIN account_journal journal ON (journal.id=st.journal_id)
                        LEFT JOIN pos_order o ON (o.id=st_line.pos_statement_id)

                        LEFT JOIN pos_session session ON (session.id=o.session_id)
                    WHERE
                        journal.debt=true
                        and  -st_line.amount<0

                         AND to_char(date_trunc('day',st_line.date),'YYYY-MM-DD')::date between %s and %s
    				and st_line.company_id=%s




                               group by st_line.amount ,session.id

                               ) as dd

                                                        '''

        self.env.cr.execute(query, (date_start, date_end, company_id))
        for row in self.env.cr.dictfetchall():
            sl += 1

            res = {

                'credit': row['amount'] if row['amount'] else 0,

            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    # def get_credit(self, data):
    #
    #     lines = []
    #     date_start = data['form']['date_start']
    #     date_end = data['form']['date_end']
    #     company_id = data['form']['branch_ids']
    #     counter_only = data['form']['counter_only']
    #     pos_config_ids = data['form']['pos_config_ids']
    #     credit = 0
    #
    #     invoice = self.env['account.invoice'].search(
    #             [('date_invoice', '>=', date_start), ('date_invoice', '<=', date_end),
    #              ('company_id', '=', company_id),
    #              ('state', 'in', ['draft', 'open']), ('type', '=', 'out_invoice')])
    #     for order in invoice:
    #         if order.state == 'draft':
    #                 credit += order.amount_total
    #         if order.state == 'open':
    #                 credit += order.residual
    #     res = {
    #         'credit': credit,
    #     }
    #
    #     lines.append(res)
    #
    #     if lines:
    #         return lines
    #     else:
    #         return []

    def get_cash_wise(self, data, config_id):
        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        if counter_only:
            cash = 0
            sessions_ids = self.env['pos.session'].search([

                ('config_id', '=', config_id)])
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done']),
                                                      ('session_id', 'in', sessions_ids.ids)])

            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])
                for account in pos_account:
                    if account.journal_id.type == 'cash' and account.journal_id.debt == False:
                        cash += account.amount

        res = {
            'cash': cash,
        }

        # lines.append(res)

        if res:
            return res
        else:
            return []

    def get_card_wise(self, data, config_id):

        lines = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        if counter_only:
            card = 0
            sessions_ids = self.env['pos.session'].search([

                ('config_id', '=', config_id)])
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done']),
                                                      ('session_id', 'in', sessions_ids.ids)])

            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])
                for account in pos_account:
                    if account.journal_id.type == 'bank':
                        card += account.amount

        res = {
            'card': card,
        }

        # lines.append(res)

        if res:
            return res
        else:
            return []

    def get_config(self, data):
        lines = []
        configs={}
        config = self.env['pos.config'].browse(data['form']['pos_config_ids'])
        for pfg in config:
            configs[pfg.id]=pfg.name


        lines.append(configs)

        if lines:
            return lines
        else:
            return []

    def get_ret(self, data):
        lines = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        if counter_only:
            ret = 0
            sessions_ids = self.env['pos.session'].search([

                ('config_id', 'in', pos_config_ids)])
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done']),
                                                      ('session_id', 'in', sessions_ids.ids)])

            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])

                for order_line in order.lines:
                    if order_line.price_subtotal_incl < 0 and order_line.product_id.name != "Discount":
                        ret += order_line.price_subtotal_incl

        else:

            ret = 0
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done'])])
            account_invoice = self.env['account.invoice'].search(
                [('date_invoice', '>=', date_start), ('date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('state', 'in', ['paid', 'open']), ('type', '=', 'out_invoice')])
            # for invoice in account_invoice:
            #     for i in invoice.payment_move_line_ids:
            #         account_move_line = self.env['account.move.line'].search(
            #             [('id', '=', i.id), ('journal_id.type', '=', 'cash'), ('move_id.state', '=', 'posted')])
            #         for j in account_move_line:
            #             cash += j.credit

            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])

                for order_line in order.lines:
                    if order_line.price_subtotal_incl < 0 and order_line.product_id.name != "Discount":
                        ret += order_line.price_subtotal_incl
        res = {
            'ret': ret,
        }

        lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_ret1(self, data, config_id):
        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        if counter_only:
            ret = 0
            sessions_ids = self.env['pos.session'].search([

                ('config_id', '=', config_id)])
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done']),
                                                      ('session_id', 'in', sessions_ids.ids)])

            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])
                for order_line in order.lines:
                    if order_line.price_subtotal_incl < 0 and order_line.product_id.name != "Discount":
                        ret += order_line.price_subtotal_incl

        res = {
            'ret': ret,
        }

        # lines.append(res)

        if res:
            return res
        else:
            return []


    @api.model
    def render_html(self, docids, data=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        # config = self.get_config(data)
        # configures = self.env['pos.config'].browse(pos_config_ids)


        config = self.env['pos.config'].browse(pos_config_ids)

        valueone = 0
        valuetwo = 0
        valuethree = 0
        valuefour = 0
        valuefive = 0
        valuesix = 0
        valueseven = 0


        date_object_startdate = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_enddate = datetime.strptime(date_end, '%Y-%m-%d').date()

        rescash = {}
        rescard = {}
        rescashline = []
        rescardline = []
        resdebtline = []
        restakeline = []
        resputline = []
        resstartline = []
        resendline = []
        totalline = []
        retwise=[]

        get_opening = self.get_opening(data)
        get_total_sale = self.get_total_sale(data)
        get_totalputmoney = self.get_totalputmoney(data)
        get_total_takemoney = self.get_total_takemoney(data)
        get_totstartbal = self.get_totstartbal(data)
        get_totalendbal = self.get_totalendbal(data)
        get_cash = self.get_cash(data)
        get_card = self.get_card(data)
        get_credit = self.get_credit(data)
        get_ret=(self.get_ret(data))




        if counter_only and pos_config_ids:
            for pfg in config:
                rescash = self.get_cash_wise(data, pfg.id)
                rescard=(self.get_card_wise(data, pfg.id))
                resdebt=(self.get_debtcard(data, pfg.id))
                restake=(self.get_take_money(data, pfg.id))
                resput=(self.get_put_money(data, pfg.id))
                resstart=(self.get_startbal(data, pfg.id))
                resendl=(self.get_endbal(data, pfg.id))
                retw = (self.get_ret1(data,pfg.id))




                rescashline.append(self.get_cash_wise(data, pfg.id))
                rescardline.append(self.get_card_wise(data, pfg.id))
                resdebtline.append(self.get_debtcard(data, pfg.id))
                restakeline.append(self.get_take_money(data, pfg.id))
                resputline.append(self.get_put_money(data, pfg.id))
                resstartline.append(self.get_startbal(data, pfg.id))
                resendline.append(self.get_endbal(data, pfg.id))
                retwise.append(self.get_ret1(data,pfg.id))
                total = retw['ret']+rescash['cash'] + rescard['card'] + resdebt['debtamount']+ restake['take_money']+resput['put_money_in']+resstart['openbalance']+resendl['endbalance']
                # numbers = map(int, numbers)
                totalline.append(total)







        docargs = {

            'counter_only': counter_only,
            'config': config,
            # 'configures': configures,
            'data': data['form'],
            'doc_ids': self.ids,
            'date_start': date_object_startdate,
            'date_end': date_object_enddate,
            'data': data['form'],
            'pos_config_ids': pos_config_ids,
            'config': config,
            'valueone': resdebtline if resdebtline else 0,
            'valuetwo': restakeline if restakeline else 0,
            'valuethree': resputline if resputline else 0,
            'counter_only': counter_only,

            'valuefour': rescashline if rescashline else 0,
            'valuefive': rescardline if rescardline else 0,
            'valuesix': resstartline if resstartline else 0,
            'valueseven': resendline if resendline else 0,
            'get_ret':get_ret if get_ret else 0,



            'get_cash': get_cash if get_cash else 0,
            'get_card': get_card if get_card else 0,
            'get_credit': get_credit if get_credit else 0,
            'get_opening': get_opening if get_opening else 0,
            'get_total_sale': get_total_sale if get_total_sale else 0,
            'get_totalputmoney': get_totalputmoney if get_totalputmoney else 0.,
            'get_total_takemoney': get_total_takemoney if get_total_takemoney else 0,
            'get_totstartbal': get_totstartbal if get_totstartbal else 0,
            'get_totalendbal': get_totalendbal if get_totalendbal else 0,
            'totalline':totalline if totalline else 0,
            'retwise':retwise if retwise else 0

        }







        # docargs = {




            # 'get_put_money':get_put_money if get_put_money else 0,
            # 'get_take_money':get_take_money if get_take_money else 0,
        #     'get_cash_wise':get_cash_wise if get_cash_wise else 0,
        #     'get_card_wise':get_card_wise if get_card_wise else 0,
        #     'get_debtcard':get_debtcard if get_debtcard else 0,
        #     'get_endbal':get_endbal if get_endbal else 0,
        #     'get_startbal':get_startbal if get_startbal else 0,
        #     'get_saletotal':get_saletotal if get_saletotal else 0,
        #
        #
        #
        #     # 'journal': journal,
        #
        #
        #
        # }

        return self.env['report'].render('consolidated_sale_xls.sale_report_pdf', docargs)





