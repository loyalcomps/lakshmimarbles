from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime,date

class ConsolidatedsaleXls(ReportXlsx):

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

    def get_put_money(self, data,config_id):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        sl = 0

        if counter_only:
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
            self.env.cr.execute(query, (date_start, date_end,config_id,company_id,
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

    def get_totalputmoney(self,data):

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
        self.env.cr.execute(query, (date_start, date_end,company_id,
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

    def get_take_money(self, data,config_id):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        sl = 0

        if counter_only:
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
            self.env.cr.execute(query, (date_start, date_end,config_id,company_id
                                    ))
            for row in self.env.cr.dictfetchall():
                sl += 1
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
    def get_total_takemoney(self,data):

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
        self.env.cr.execute(query, (date_start, date_end,company_id,
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




    def get_saletotal(self, data,config_id):
        lines = []
        res ={}

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
                                    where  po.state in ('done','paid','invoiced') and

        				po.company_id = %s
        				and CAST(pos.start_at AS DATE) between %s and %s
                                    and pos.config_id = %s
                                    GROUP BY CAST(pos.start_at AS DATE),abs.amount,po.name,aj.type ,pos.name
                                    ) as dd 
                                    GROUP BY dd.start_at,dd.pname order by dd.start_at,dd.pname


                                           '''

        self.env.cr.execute(query, (company_id, date_start, date_end,config_id,

                                        ))
        for row in self.env.cr.dictfetchall():
            sl += 1

            stotal= row['total'] if row['total'] else 0


                # dates = datetime.strptime(row['sale_date'], '%Y-%m-%d').date()

            res = {
                    'total': stotal,

                }

            lines.append(res)

        if lines:
            return lines
        else:
            return []




    def get_startbal(self, data,config_id):
        lines = []
        res ={}

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['branch_ids']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        if counter_only:




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

            self.env.cr.execute(query, ( date_start, date_end, config_id,company_id))
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

    def get_totstartbal(self,data):

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

        self.env.cr.execute(query, (date_start, date_end,company_id))
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

    def get_endbal(self, data,config_id):
            lines = []
            res = {}

            date_start = data['form']['date_start']
            date_end = data['form']['date_end']
            company_id = data['form']['branch_ids']
            counter_only = data['form']['counter_only']
            pos_config_ids = data['form']['pos_config_ids']

            if counter_only:




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

                self.env.cr.execute(query, (date_start, date_end, config_id,company_id))
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

    def get_totalendbal(self,data):

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

        self.env.cr.execute(query, (date_start, date_end,company_id))
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




    def get_debtcard(self,data,config_id):

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

        self.env.cr.execute(query, (date_start, date_end,config_id,company_id))
        for row in self.env.cr.dictfetchall():
            sl += 1

            res = {

                'debtamount': row['amount'] if row['amount'] else 0,

            }
            lines.append(res)
        if lines:
            return lines
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
                        [('id', '=', i.id), ('journal_id.type', '=', 'cash'),('journal_id.debt', '=', False), ('move_id.state', '=', 'posted')])
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

        self.env.cr.execute(query, (date_start, date_end,company_id))
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

        lines.append(res)

        if lines:
            return lines
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

        lines.append(res)

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

        lines.append(res)

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Sales Report'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 25)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 20)
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
        sheet.set_column(21, 21, 30)
        sheet.set_column(22, 22, 20)
        sheet.set_column(23, 23, 20)
        sheet.set_column(24, 24, 20)

        date_start = data['form']['date_start']

        date_end = data['form']['date_end']

        pos_config_ids = data['form']['pos_config_ids']

        counter_only = data['form']['counter_only']

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        company = self.env['res.company'].browse(data['form']['branch_ids']).name

        company_address = self.env['res.company'].browse(data['form']['branch_ids']).street
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True})

        format2 = workbook.add_format(
            {'font_size': 16, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True})

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
        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        # sheet.write('A4' "Card", blue_mark)
        # sheet.write('A6', "Credit", blue_mark)


        if counter_only and pos_config_ids:
            sheet.merge_range('E1:F1',"company" , blue_mark2)

            sheet.merge_range('B2:C2', "Consolidated Sale Report ", blue_mark)


            sheet.write('A4', "Opening Balance", blue_mark)

            sheet.write('A6', "Cash", blue_mark)
            sheet.merge_range('E2:F2', date_object_date_start.strftime('%d-%m-%Y') + ' - ' + date_object_date_end.strftime('%d-%m-%Y'), format1)
            sheet.write('D2', "Date :-", orange_mark)
            sheet.write('A8', "Card", blue_mark)
            sheet.write('A10', "Credit", blue_mark)
            sheet.write('A12', "Put Money In", blue_mark)
            sheet.write('A14', "Take Money", blue_mark)
            sheet.write('A16', "Return", blue_mark)
            sheet.write('A18', "Closing Balance", blue_mark)
            line_column = 1

            config = self.env['pos.config'].browse(pos_config_ids)
            for pfg in config:


                line_row = 3
                sheet.write(2, line_column, str(pfg.name), font_size_8)

                if self.get_startbal(data, pfg.id):
                    for line in self.get_startbal(data,pfg.id):
                        sheet.write(line_row, line_column, line['openbalance'], font_size_8)
                        line_row = line_row + 1

                    line_row = line_row + 1
                else:
                    for line in self.get_startbal(data, pfg.id):
                        sheet.write(line_row, line_column, 0, font_size_8)
                        line_row = line_row + 1

                    line_row = line_row + 1

                for line in self.get_cash_wise(data,pfg.id):
                    sheet.write(line_row, line_column, line['cash'], font_size_8)
                    line_row = line_row + 1

                line_row = line_row + 1
                for line in self.get_card_wise(data,pfg.id):
                    sheet.write(line_row, line_column, line['card'], font_size_8)
                    line_row = line_row + 1

                line_row = line_row + 1
                for line in self.get_debtcard(data,pfg.id):
                    sheet.write(line_row, line_column, line['debtamount'], font_size_8)
                    line_row = line_row + 1

                line_row = line_row + 1
                for line in self.get_put_money(data,pfg.id):
                    sheet.write(line_row, line_column, line['put_money_in'], font_size_8)
                    line_row = line_row + 1

                line_row = line_row + 1
                for line in self.get_take_money(data,pfg.id):
                    sheet.write(line_row, line_column, line['take_money'], font_size_8)
                    line_row = line_row + 1

                line_row = line_row + 1
                for line in self.get_ret1(data,pfg.id):
                    sheet.write(line_row, line_column, line['ret'], font_size_8)
                    line_row = line_row + 1

                line_row = line_row + 1
                for line in self.get_endbal(data,pfg.id):
                    sheet.write(line_row, line_column, line['endbalance'], font_size_8)
                    line_row = line_row + 1

                line_row = line_row + 1

                line_column += 1
                # total_cell_range = xl_range(3, line_column-1, line_row-1, line_column - 1)
                # sheet.write_formula(line_row, line_column-1, '=SUM(' + total_cell_range + ')', format2)
            sheet.write(2, line_column,"Total", font_size_8)
            total_cell_range = xl_range(3, 1, 3, line_column-1)
            total_cell_range1 = xl_range(5, 1, 5, line_column-1)
            total_cell_range2 = xl_range(7, 1, 7, line_column-1)
            total_cell_range3 = xl_range(9, 1, 9, line_column - 1)
            total_cell_range4 = xl_range(11, 1, 11, line_column - 1)
            total_cell_range5 = xl_range(13, 1, 13, line_column - 1)
            total_cell_range6 = xl_range(15, 1, 15, line_column - 1)
            total_cell_range7 = xl_range(17, 1, 17, line_column - 1)




            sheet.write_formula(3, line_column, '=SUM(' + total_cell_range + ')', format2)
            sheet.write_formula(5, line_column, '=SUM(' + total_cell_range1 + ')', format2)
            sheet.write_formula(7, line_column, '=SUM(' + total_cell_range2 + ')', format2)
            sheet.write_formula(9, line_column, '=SUM(' + total_cell_range3 + ')', format2)
            sheet.write_formula(11, line_column, '=SUM(' + total_cell_range4 + ')', format2)
            sheet.write_formula(13, line_column, '=SUM(' + total_cell_range5 + ')', format2)
            sheet.write_formula(15, line_column, '=SUM(' + total_cell_range6 + ')', format2)
            sheet.write_formula(17, line_column, '=SUM(' + total_cell_range7 + ')', format2)






        else:

            sheet.merge_range('A1:B1', "Consolidated Sale Report ", format1)
            sheet.write('C1', "DATE :-", format1)
            sheet.merge_range('D1:E1', date_start + ' - ' + date_end, format1)

            sheet.write('A3', "Open Balance", blue_mark)
            line_row = 3
            line_column = 1
            for line in self.get_totstartbal(data):
                sheet.write(line_row, line_column, line['openbalance'], font_size_8)
                line_row = line_row + 1
                line_column = 0

            sheet.write(line_row, line_column, "Cash", blue_mark)
            line_row = line_row + 1
            line_column = 1
            for line in self.get_cash(data):
                sheet.write(line_row, line_column, line['cash'], font_size_8)
                line_row = line_row + 1
                line_column = 0


            sheet.write(line_row, line_column, "Card", blue_mark)
            line_row = line_row + 1
            line_column = 1
            for line in self.get_card(data):
                sheet.write(line_row, line_column, line['card'], font_size_8)
                line_row = line_row + 1
                line_column = 0
            sheet.write(line_row, line_column, "Credit", blue_mark)
            line_row = line_row + 1
            line_column = 1
            for line in self.get_credit(data):
                sheet.write(line_row, line_column, line['credit'], font_size_8)
                line_row = line_row + 1
                line_column = 0
            sheet.write(line_row, line_column, "Put Money In", blue_mark)
            line_row = line_row + 1
            line_column = 1
            for line in self.get_totalputmoney(data):
                sheet.write(line_row, line_column, line['put_money_in'], font_size_8)
                line_row = line_row + 1
                line_column = 0
            sheet.write(line_row, line_column, "Take Money Out", blue_mark)
            line_row = line_row + 1
            line_column = 1
            for line in self.get_total_takemoney(data):
                sheet.write(line_row, line_column, line['take_money'], font_size_8)
                line_row = line_row + 1
                line_column = 0

            sheet.write(line_row, line_column, "Return", blue_mark)
            line_row = line_row + 1
            line_column = 1
            for line in self.get_ret(data):
                sheet.write(line_row, line_column, line['ret'], font_size_8)
                line_row = line_row + 1
                line_column = 0

            sheet.write(line_row, line_column, "Closing Balance", blue_mark)
            line_row = line_row + 1
            line_column = 1
            for line in self.get_totalendbal(data):
                sheet.write(line_row, line_column, line['endbalance'], font_size_8)
                line_row = line_row + 1
                line_column = 0

            sheet.write(line_row, 0, "TOTAL", format1)

            total_cell_range = xl_range(3, 1, line_row - 1, 1)
            sheet.write_formula(line_row, 1, '=SUM(' + total_cell_range + ')', format2)

            # sheet.write(line_row, 0, "TOTAL", format1)
            #
            # total_cell_range = xl_range(18, line_column, 18, line_column - 1)
            # total_cell_range7 = xl_range(17, 1, 17, line_column - 1)

            # total_cell_range7 = xl_range(17, 1, 17, line_column - 1)

            # sheet.write_formula(3, line_column, '=SUM(' + total_cell_range + ')', format2)

            # sheet.write_formula(18, line_column, '=SUM(' + total_cell_range + ')', format2)

            # total_cell_range = xl_range(3, 1, line_row - 1, 1)
            # sheet.write_formula(line_row, 1, '=SUM(' + total_cell_range + ')', format2)





ConsolidatedsaleXls('report.consolidated_sale_xls.consolidated_sale_xls.xlsx', 'account.move')
