import time
from odoo import api, models, _
from datetime import datetime


class Reportsales(models.AbstractModel):
    _name = 'report.qlty_salesreport_xls.qlty_salesreport_pdf'

    def get_cash(self, data):

        lines = []
        invoice_id = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        cr = 0
        am1=0
        # am2=[]
        # am3=[]

        if counter_only:

            am1=0
            am2 = 0
            am3 = 0
        else:

            res6 = '''
            
            
            
            
                                           select
                                COALESCE(sum(CASE v.payment_amount WHEN v.payment_amount THEN v.payment_amount ELSE 0 END ))  as amount 

                                from( select (ap.amount) as payment_amount
                					from account_payment as ap
                                                        			left join account_journal as aj on(aj.id=ap.journal_id)
                                                                    left join pos_session as ps on(ps.id=ap.pos_counter_ids)
                                                        			left join pos_config as pc on(pc.id=ps.config_id)
                                                        			left join account_invoice_payment_rel as aa on (aa.payment_id=ap.id)
        									left join account_invoice as a on aa.invoice_id=a.id	
                                                                			where aj.type='cash' and aj.name<>'Round off' and ap.state='posted' 
                                                                			
                                                                			and ap.payment_type='inbound' and aj.company_id = %s and ap.pos_counter_ids is not null
                                                                			 and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
                                                                			 ::date between %s and %s 
                                                                			 group by pc.id,ap.amount,a.id) v


                                                        '''

            self.env.cr.execute(res6, ( company_id, date_start, date_end,

                                       ))
            for row1 in self.env.cr.dictfetchall():
                am2 = (row1['amount'] if row1['amount'] else 0)
                # am2.append(row1['amount'])
                # card = (row['bank'] if row['bank'] else 0)

            res4 = '''

              select sum(absl.amount) as amount,aj.type from account_bank_statement_line as absl
            left join account_journal as aj on aj.id =  absl.journal_id
            where aj.type='cash' and absl.company_id=%s and absl.pos_statement_id in (select id from pos_order where session_id in
            (select id from pos_session where to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s
            and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date between %s and %s )
            ) and aj.used_for_rounding is not true
            group by aj.type
                                            '''

            self.env.cr.execute(res4, ( company_id,date_start, date_end,
                                        date_start, date_end,

                                        ))
            for row in self.env.cr.dictfetchall():
                am1 += (row['amount'] if row['amount'] else 0)
                # card = (row['bank'] if row['bank'] else 0)

            # res4 = '''
            #
            #

            #             select sum(absl.amount) as amount,aj.type from account_bank_statement_line as absl
            # left join account_journal as aj on aj.id =  absl.journal_id
            # where aj.type='cash' and absl.company_id=%s and absl.pos_statement_id in (select id from pos_order where session_id in
            # (select id from pos_session where to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s
            # and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date between %s and %s )
            # ) and aj.used_for_rounding is not true
            # group by aj.type

            #
            #
            #
            #             '''
            #
            #     self.env.cr.execute(res4, (company_id, date_start, date_end, date_start, date_end,
            #
            #                                ))
            #     for row1 in self.env.cr.dictfetchall():
            #         # am1.append(row1['amount'])
            #         am1 = (row1['amount'] if row1['amount'] else 0)
            #         # am1.append(am6)
            #         # if am1 == []:
            #         #     am1 = 0

            re5 = '''


                                          select 
                                            COALESCE(sum(CASE k.amr WHEN k.amr THEN k.amr ELSE 0 END ))  as amount


                                           from(select 
                                                 --COALESCE((CASE a.pos_config_ids WHEN a.pos_config_ids THEN a.pos_config_ids ELSE 0 END ))  as id,

                                               a.pos_config_ids as id,
                                                --COALESCE(sum(CASE apr.amount WHEN apr.amount THEN apr.amount ELSE 0 END ))  as amr
                                                (apr.amount) as amr 
                                                from account_partial_reconcile as apr

                                    	left join account_move_line as aml on aml.id=apr.credit_move_id
                                    	left join account_move as am on am.id=aml.move_id
                                    	left join account_journal as aj on aj.id=am.journal_id
                                    	left join account_account as aa on aml.account_id=aa.id
                                    		left join account_invoice as a on (a.account_id=aa.id)


                                    	where aj.company_id=%s and aj.type='cash' and aj.name<>'Round off' and a.partial_payment_remark is not null and a.state='paid'
                                    	and a.pos_config_ids is not null 
                                                			 and  to_char(date_trunc('day',apr.create_date),'YYYY-MM-DD')
                                                			 ::date between %s and %s and aml.payment_id not in ( select ap.id from account_payment as ap
                                                                                    			left join account_journal as aj on(aj.id=ap.journal_id)
                                                                                    			left join pos_session as ps on(ps.id=ap.pos_counter_ids)
                                                                                                left join pos_config as pc on(pc.id=ps.config_id)

                                                                                    			where aj.name<>'Round off' and ap.payment_type='inbound' and aj.company_id = %s
                                                                                    			 and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
                                                                                    			 ::date between %s and %s
                                                                                    			 )

                                                                                    			 group by a.pos_config_ids,apr.amount)k

                                '''

            self.env.cr.execute(re5, (
                company_id,date_start, date_end,
                company_id, date_start, date_end
            ))
            for row4 in self.env.cr.dictfetchall():
                am3=(row4['amount']) if row4['amount'] else 0.0


        res = {
            'cash': am1+am2+am3,
        }

        lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_card(self, data):

        lines = []
        invoice_id = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        am1 = 0
        # am2 = []
        # am3 = []

        if counter_only:

            cr=13444
            am1=0
            am2=0
            am3=0
        else:

            res6 = '''

                                    select
                                    COALESCE(sum(CASE v.payment_amount WHEN v.payment_amount THEN v.payment_amount ELSE 0 END ))  as amount 

                                    from( select (ap.amount) as payment_amount
                    					from account_payment as ap
                                                            			left join account_journal as aj on(aj.id=ap.journal_id)
                                                            			left join pos_session as ps on(ps.id=ap.pos_counter_ids)
                                                                        left join pos_config as pc on(pc.id=ps.config_id)
                                                            			left join account_invoice_payment_rel as aa on (aa.payment_id=ap.id)
            									left join account_invoice as a on aa.invoice_id=a.id	
                                                                    			where aj.type='bank' and aj.name<>'Round off' and ap.state='posted' 
                                                                    			
                                                                    			and ap.payment_type='inbound' and aj.company_id = %s and ap.pos_counter_ids is not null
                                                                    			 and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
                                                                    			 ::date between %s and %s 
                                                                    			 group by pc.id,ap.amount,a.id) v
                                                '''

            self.env.cr.execute(res6, (company_id, date_start, date_end,

                                       ))
            for row1 in self.env.cr.dictfetchall():
                am2=(row1['amount']) if row1['amount'] else 0.0
                # card = (row['bank'] if row['bank'] else 0)

            res4 = '''

                          select sum(absl.amount) as amount,aj.type from account_bank_statement_line as absl
            left join account_journal as aj on aj.id =  absl.journal_id
            where aj.type='bank' and absl.company_id=%s and absl.pos_statement_id in (select id from pos_order where session_id in
            (select id from pos_session where to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s
            and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date between %s and %s )
            ) and aj.used_for_rounding is not true
            group by aj.type
                                            '''

            self.env.cr.execute(res4, ( company_id,date_start, date_end,
                                        date_start, date_end,
                                       ))
            for row in self.env.cr.dictfetchall():
                am1 += (row['amount'] if row['amount'] else 0)
                # am6 = (row1['amount'] if row1['amount'] else 0)
                # am1.append(am6)
                # if am1 == []:
                #     am1 = 0

                # card = (row['bank'] if row['bank'] else 0)

            re5 = '''


                                  select 
                                    COALESCE(sum(CASE k.amr WHEN k.amr THEN k.amr ELSE 0 END ))  as amount


                                   from(select 
                                         --COALESCE((CASE a.pos_config_ids WHEN a.pos_config_ids THEN a.pos_config_ids ELSE 0 END ))  as id,

                                       a.pos_config_ids as id,
                                        --COALESCE(sum(CASE apr.amount WHEN apr.amount THEN apr.amount ELSE 0 END ))  as amr
                                        (apr.amount) as amr 
                                        from account_partial_reconcile as apr

                            	left join account_move_line as aml on aml.id=apr.credit_move_id
                            	left join account_move as am on am.id=aml.move_id
                            	left join account_journal as aj on aj.id=am.journal_id
                            	left join account_account as aa on aml.account_id=aa.id
                            		left join account_invoice as a on (a.account_id=aa.id)


                            	where aj.company_id=%s and aj.type='bank' and aj.name<>'Round off' and a.partial_payment_remark is not null and a.state='paid'
                            	and a.pos_config_ids is not null
                                        			 and  to_char(date_trunc('day',apr.create_date),'YYYY-MM-DD')
                                        			 ::date between %s and %s and aml.payment_id not in ( select ap.id from account_payment as ap
                                                                            			left join account_journal as aj on(aj.id=ap.journal_id)
                                                                            			left join pos_session as ps on(ps.id=ap.pos_counter_ids)
                                                                                        left join pos_config as pc on(pc.id=ps.config_id)
                                                                            			where aj.name<>'Round off' and ap.payment_type='inbound' and aj.company_id = %s
                                                                            			 and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
                                                                            			 ::date between %s and %s
                                                                            			 )

                                                                            			 group by a.pos_config_ids,apr.amount)k

                        '''

            self.env.cr.execute(re5, (
                company_id, date_start, date_end,
                company_id, date_start, date_end
            ))
            for row4 in self.env.cr.dictfetchall():
                am3=(row4['amount']) if row4['amount'] else 0.0

            # if config_id == coun_id:
            #     cr += (row['bank'] if row['bank'] else 0.0)
            # else:
            #     cr = 0


        res = {
            'card': am1+am2+am3,
        }

        lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_credit(self, data):

        lines = []
        # invoice_id = []
        # invoice_remark = []
        # residual = []
        # amount_total = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']

        pos_config_ids = data['form']['pos_config_ids']


        if counter_only:

            credit=13444
        else:
            credit=0


            # re5 = '''
            #
            #     select sum(g.cash) as credit
            #      from( SELECT dd.amount_total-dd.cash as cash,dd.config_id from
            #
            #             (select COALESCE(round(sum(CASE st_line.amount WHEN st_line.amount THEN st_line.amount ELSE 0 END ),0))  as cash,
            #             COALESCE(round(CASE a.amount_total WHEN a.amount_total THEN a.amount_total ELSE 0 END ),0)  as amount_total,
            #
            #                     --sum(st_line.amount) as cash,
            #                     session.config_id as config_id
            #                    -- (a.amount_total)
            #                FROM account_bank_statement_line as st_line
            #                     LEFT JOIN account_bank_statement st ON (st.id=st_line.statement_id)
            #                     LEFT JOIN account_journal journal ON (journal.id=st.journal_id)
            #                     LEFT JOIN pos_order o ON (o.id=st_line.pos_statement_id)
            #                     LEFT JOIN account_invoice as a ON (a.id=o.invoice_id)
            #
            #                     LEFT JOIN pos_session session ON (session.id=o.session_id)
            #                 WHERE
            #
            #                     st_line.amount>0 and o.invoice_remark is not null and  o.picking_id is null and
            #
            #
            #                       to_char(date_trunc('day',st_line.date),'YYYY-MM-DD')::date between %s and %s
            #                 and st_line.company_id=%s
            #
            #                            group by session.config_id,a.id)dd group by dd.amount_total-dd.cash,dd.config_id)g
            #
            #                             '''
            #
            # self.env.cr.execute(re5, (date_start, date_end, company_id,
            #
            #                           ))
            # for row in self.env.cr.dictfetchall():
            #     # coun_id = (row['id'] if row['id'] else 0)
            #     credit = (row['credit'] if row['credit'] else 0)

        res = {
            'credit': credit if credit else 0.0,
        }

        lines.append(res)

        if lines:
            return lines
        else:
            return []


    def get_credit_so(self, data, config_id):
        lines = []
        # invoice_id = []
        # invoice_remark = []
        # residual = []
        # amount_total = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        cr = 0
        # cre = 0

        if counter_only:
            cr=0

#             re5 = '''
#
# select sum(g.cash) as credit,g.id as id from( SELECT dd.amount_total-dd.cash as cash,dd.config_id as id from
#
#         			(select COALESCE(round(sum(CASE st_line.amount WHEN st_line.amount THEN st_line.amount ELSE 0 END ),0))  as cash,
#         			COALESCE(round(CASE a.amount_total WHEN a.amount_total THEN a.amount_total ELSE 0 END ),0)  as amount_total,
#
#                             --sum(st_line.amount) as cash,
#                             session.config_id as config_id
#                            -- (a.amount_total)
#                        FROM account_bank_statement_line as st_line
#                             LEFT JOIN account_bank_statement st ON (st.id=st_line.statement_id)
#                             LEFT JOIN account_journal journal ON (journal.id=st.journal_id)
#                             LEFT JOIN pos_order o ON (o.id=st_line.pos_statement_id)
#                             LEFT JOIN account_invoice as a ON (a.id=o.invoice_id)
#
#                             LEFT JOIN pos_session session ON (session.id=o.session_id)
#                         WHERE
#
#                             st_line.amount>0 and o.invoice_remark is not null and  o.picking_id is null and
#
#
#                               to_char(date_trunc('day',st_line.date),'YYYY-MM-DD')::date between %s and %s
#         				and st_line.company_id=%s and session.config_id in %s
#
#                                    group by session.config_id,a.id)dd group by dd.amount_total-dd.cash,dd.config_id)g group by g.id
#                     '''
#
#             self.env.cr.execute(re5, ( date_start, date_end, company_id,config_id,
#
#                                       ))
#             for row in self.env.cr.dictfetchall():
#
#                 coun_id = (row['id'] if row['id'] else 0)
#                 # card = (row['bank'] if row['bank'] else 0)
#
#                 if config_id == coun_id:
#                     cr += (row['credit'] if row['credit'] else 0.0)
#                 else:
#                     cr = 0
#

        res = {
            'credit': cr,
        }

        # lines.append(res)

        if res:
            return res
        else:
            return []

    def get_card_so(self, data, config_id):
        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        credit = 0

        if counter_only:

            sessions_ids = self.env['pos.session'].search([

                ('config_id', '=', config_id)])
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done']),
                                                      ('session_id', 'in', sessions_ids.ids)])

            st_line_ids = self.env["account.bank.statement.line"].search(
                [('pos_statement_id', 'in', pos_order.ids)]).ids
            if st_line_ids:
                self.env.cr.execute("""
                            SELECT COALESCE(sum(amount),'0') total
                FROM account_bank_statement_line AS absl,
                     account_bank_statement AS abs,
                     account_journal AS aj 
                WHERE absl.statement_id = abs.id
                    AND abs.journal_id = aj.id and aj.type ='cash'
                    --and aj.debt = 'true'
                    AND absl.id IN %s 
                        """, (tuple(st_line_ids),))
                credit = self.env.cr.dictfetchall()
            else:
                credit = [{'total': 0.0}]

        res = {
            'credit': credit[0]['total'] if credit else 0.0,
        }

        # lines.append(res)

        if res:
            return res
        else:
            return []

    def get_cash_wise(self, data, config_id):
        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        # date_start=
        cash = 0

        # cr = 0
        # cm = 0
        cr=0
        # am1 = []
        # am2 = []
        # am3 = []
        am1=0

        if counter_only:

            res6 = '''

                                select
                                COALESCE(sum(CASE v.payment_amount WHEN v.payment_amount THEN v.payment_amount ELSE 0 END ))  as amount 

                                from( select (ap.amount) as payment_amount
                					from account_payment as ap
                                                        			left join account_journal as aj on(aj.id=ap.journal_id)
                                                        			left join pos_session as ps on(ps.id=ap.pos_counter_ids)
                                                                    left join pos_config as pc on(pc.id=ps.config_id)
                                                        			left join account_invoice_payment_rel as aa on (aa.payment_id=ap.id)
        									left join account_invoice as a on aa.invoice_id=a.id	
                                                                			where aj.type='cash' and aj.name<>'Round off' and ap.state='posted' 
                                                                			and pc.id = %s
                                                                			and ap.payment_type='inbound' and aj.company_id = %s and ap.pos_counter_ids is not null
                                                                			 and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
                                                                			 ::date between %s and %s 
                                                                			 group by pc.id,ap.amount,a.id) v
                                            '''

            self.env.cr.execute(res6, ((config_id), company_id,date_start, date_end,

                                       ))
            for row1 in self.env.cr.dictfetchall():
                am2=(row1['amount']) if row1['amount'] else 0.0
                if row1['amount']==None:
                    am2=0
                # card = (row['bank'] if row['bank'] else 0)

            res4='''



                        select sum(absl.amount) as amount,aj.type from account_bank_statement_line as absl
            left join account_journal as aj on aj.id =  absl.journal_id
            where aj.type='cash' and absl.company_id=%s and absl.pos_statement_id in (select id from pos_order where session_id in
            (select id from pos_session where config_id =%s and to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s
            and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date between %s and %s )
            ) and aj.used_for_rounding is not true
            group by aj.type




            '''

            self.env.cr.execute(res4, (company_id, (config_id), date_start, date_end,date_start, date_end,

                                       ))
            for row1 in self.env.cr.dictfetchall():
                am1 += (row1['amount'] if row1['amount'] else 0)

                # am1+=row1['amount']
                # am1.append(am6)
                if row1['amount']==None:
                    am1=0
                # else:
                #     am1[0]




            # res4 = '''
            #
            #               SELECT
            #                                                     dd.con_id as config,
            #
            #                                                 COALESCE(sum(CASE dd.balance WHEN dd.balance THEN dd.balance ELSE 0 END ))  as amount
            #
            #
            #                                      from
            #                                     (
            #
            #             		SELECT
            #
            #                                 st_line.amount as balance,
            #                                 session.config_id as con_id
            #
            #
            #
            #                            FROM account_bank_statement_line as st_line
            #                                             LEFT JOIN account_bank_statement st ON (st.id=st_line.statement_id)
            #                                             LEFT JOIN pos_order o ON (o.id=st_line.pos_statement_id)
            #                                             LEFT JOIN pos_session session ON (session.id=st.pos_session_id)
            #
            #                                            LEFT JOIN account_journal journal ON (journal.id=st_line.journal_id)
            #                                         WHERE
            #                                               st_line.pos_statement_id is not null and st_line.ref is not null and
            #                                               session.config_id in %s and
            #                                                 journal.type='cash' and journal.name<>'Round off' and
            #
            #                                                   to_char(date_trunc('day',st_line.date),'YYYY-MM-DD')::date between %s and %s
            #                             				and st_line.company_id=%s
            #
            #
            #
            #
            #                                                    group by st_line.amount ,session.id,session.config_id
            #
            #                                        ) as dd group by dd.con_id
            #
            #
            #
            #                     '''
            #
            # self.env.cr.execute(res4, (tuple(pos_config_ids), date_start, date_end, company_id,
            #
            #                            ))
            # for row in self.env.cr.dictfetchall():
            #     # am1 = (row['amount'] if row['amount'] else 0)
            #     config = (row['config'] if row['config'] else 0.0)
            #     # if row['amount']==None:
            #     #     am1=0
            #
            #     # for i in pos_config_ids:
            #     if config_id == config:
            #         am1 += (row['amount'] if row['amount'] else 0.0)
            #
            #     else:
            #         am1=0
            #
            #     card = (row['bank'] if row['bank'] else 0)

            re5 = '''


                              select 
                                COALESCE(sum(CASE k.amr WHEN k.amr THEN k.amr ELSE 0 END ))  as amount


                               from(select 
                                     --COALESCE((CASE a.pos_config_ids WHEN a.pos_config_ids THEN a.pos_config_ids ELSE 0 END ))  as id,

                                   a.pos_config_ids as id,
                                    --COALESCE(sum(CASE apr.amount WHEN apr.amount THEN apr.amount ELSE 0 END ))  as amr
                                    (apr.amount) as amr 
                                    from account_partial_reconcile as apr

                        	left join account_move_line as aml on aml.id=apr.credit_move_id
                        	left join account_move as am on am.id=aml.move_id
                        	left join account_journal as aj on aj.id=am.journal_id
                        	left join account_account as aa on aml.account_id=aa.id
                        		left join account_invoice as a on (a.account_id=aa.id)


                        	where aj.company_id=%s and aj.type='cash' and aj.name<>'Round off' and a.partial_payment_remark is not null and a.state='paid'
                        	and a.pos_config_ids is not null and a.pos_config_ids = %s
                                    			 and  to_char(date_trunc('day',apr.create_date),'YYYY-MM-DD')
                                    			 ::date between %s and %s and aml.payment_id not in ( select ap.id from account_payment as ap
                                                                        			left join account_journal as aj on(aj.id=ap.journal_id)
                                                                        			left join pos_session as ps on(ps.id=ap.pos_counter_ids)
                                                                                    left join pos_config as pc on(pc.id=ps.config_id)

                                                                        			where aj.name<>'Round off' and ap.payment_type='inbound' and aj.company_id = %s
                                                                        			 and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
                                                                        			 ::date between %s and %s
                                                                        			 )

                                                                        			 group by a.pos_config_ids,apr.amount)k

                    '''

            self.env.cr.execute(re5, (
                company_id, config_id, date_start, date_end,
                company_id, date_start, date_end
            ))
            for row4 in self.env.cr.dictfetchall():
                am3=(row4['amount']) if row4['amount'] else 0.0
                if row4['amount']==None:
                    am3=0


        res = {
            'cash': am1+am2+am3,
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
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        # card = 0
        cr = 0
        # cm = 0
        am1=0


        if counter_only:

            res6 = '''

                        select
                        COALESCE(sum(CASE v.payment_amount WHEN v.payment_amount THEN v.payment_amount ELSE 0 END ))  as amount 
                        
                        from( select (ap.amount) as payment_amount
        					from account_payment as ap
                                                			left join account_journal as aj on(aj.id=ap.journal_id)
                                                			left join pos_session as ps on(ps.id=ap.pos_counter_ids)
                                                            left join pos_config as pc on(pc.id=ps.config_id)
                                                			left join account_invoice_payment_rel as aa on (aa.payment_id=ap.id)
									left join account_invoice as a on aa.invoice_id=a.id	
                                                        			where aj.type='bank' and aj.name<>'Round off' and ap.state='posted' 
                                                        			and pc.id = %s
                                                        			and ap.payment_type='inbound' and aj.company_id = %s and ap.pos_counter_ids is not null
                                                        			 and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
                                                        			 ::date between %s and %s 
                                                        			 group by pc.id,ap.amount,a.id) v
                                    '''

            self.env.cr.execute(res6, ((config_id),  company_id,date_start, date_end,

                                       ))
            for row1 in self.env.cr.dictfetchall():
                am2 = (row1['amount'] if row1['amount'] else 0)
                # am2.append(row1['amount'])
                if row1['amount']==None:
                    am2=0
                # am2 = (row1['amount'] if row1['amount'] else 0)
                # card = (row['bank'] if row['bank'] else 0)

            res4 = '''



                        select sum(absl.amount) as amount,aj.type from account_bank_statement_line as absl
            left join account_journal as aj on aj.id =  absl.journal_id
            where aj.type='bank' and absl.company_id=%s and absl.pos_statement_id in (select id from pos_order where session_id in
            (select id from pos_session where config_id =%s and to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date between %s and %s
            and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date between %s and %s )
            ) and aj.used_for_rounding is not true
            group by aj.type




                        '''

            self.env.cr.execute(res4, (company_id, (config_id), date_start, date_end, date_start, date_end,

                                       ))
            for row1 in self.env.cr.dictfetchall():
                if row1['amount']==None:
                    am1=0
                if row1['amount']:
                    row1['amount']
                else:
                    row1['amount']=0
            #
                am1 += (row1['amount'] if row1['amount'] else 0)
            #     # am6 = (row1['amount'] if row1['amount'] else 0)
            #     am7.append(row1['amount'])
            #     if am1 == []:
            #         am1 = 0
            #
            #     else:
            #         am1=0

                # card = (row['bank'] if row['bank'] else 0)

            # res4 = '''
            #
            #                           SELECT
            #                                                                 dd.con_id as config,
            #
            #                                                             COALESCE(sum(CASE dd.balance WHEN dd.balance THEN dd.balance ELSE 0 END ))  as amount
            #
            #
            #                                                  from
            #                                                 (
            #
            #                         		SELECT
            #
            #                                             st_line.amount as balance,
            #                                             session.config_id as con_id
            #
            #
            #
            #                                        FROM account_bank_statement_line as st_line
            #                                                         LEFT JOIN account_bank_statement st ON (st.id=st_line.statement_id)
            #                                                         LEFT JOIN pos_order o ON (o.id=st_line.pos_statement_id)
            #                                                         LEFT JOIN pos_session session ON (session.id=st.pos_session_id)
            #
            #                                                        LEFT JOIN account_journal journal ON (journal.id=st_line.journal_id)
            #                                                     WHERE
            #                                                           st_line.pos_statement_id is not null and st_line.ref is not null and
            #                                                           session.config_id in %s and
            #                                                             journal.type='bank' and journal.name<>'Round off' and
            #
            #                                                               to_char(date_trunc('day',st_line.date),'YYYY-MM-DD')::date between %s and %s
            #                                         				and st_line.company_id=%s
            #
            #
            #
            #
            #                                                                group by st_line.amount ,session.id,session.config_id
            #
            #                                                    ) as dd group by dd.con_id
            #
            #
            #
            #                                 '''
            #
            # self.env.cr.execute(res4, (tuple(pos_config_ids), date_start, date_end, company_id,
            #
            #                            ))
            # for row in self.env.cr.dictfetchall():
            #     # am1 = (row['amount'] if row['amount'] else 0)
            #     config = (row['config'] if row['config'] else 0.0)
            #     # if row['amount']==None:
            #     #     am1=0
            #
            #     # for i in pos_config_ids:
            #     if config_id == config:
            #         am1 += (row['amount'] if row['amount'] else 0.0)
            #     else:
            #         am1 = 0
            #
            #     card = (row['bank'] if row['bank'] else 0)

            re5 = '''


                      select 
                        COALESCE(sum(CASE k.amr WHEN k.amr THEN k.amr ELSE 0 END ))  as amount

                       
                       from(select 
                             --COALESCE((CASE a.pos_config_ids WHEN a.pos_config_ids THEN a.pos_config_ids ELSE 0 END ))  as id,

                           a.pos_config_ids as id,
                            --COALESCE(sum(CASE apr.amount WHEN apr.amount THEN apr.amount ELSE 0 END ))  as amr
                            (apr.amount) as amr 
                            from account_partial_reconcile as apr

                	left join account_move_line as aml on aml.id=apr.credit_move_id
                	left join account_move as am on am.id=aml.move_id
                	left join account_journal as aj on aj.id=am.journal_id
                	left join account_account as aa on aml.account_id=aa.id
                		left join account_invoice as a on (a.account_id=aa.id)


                	where aj.company_id=%s and aj.type='bank' and aj.name<>'Round off' and a.partial_payment_remark is not null and a.state='paid'
                	and a.pos_config_ids is not null and a.pos_config_ids = %s
                            			 and  to_char(date_trunc('day',apr.create_date),'YYYY-MM-DD')
                            			 ::date between %s and %s and aml.payment_id not in ( select ap.id from account_payment as ap
                                                                			left join account_journal as aj on(aj.id=ap.journal_id)
                                                                			left join pos_session as ps on(ps.id=ap.pos_counter_ids)
                                                                            left join pos_config as pc on(pc.id=ps.config_id)
                                                                			where aj.name<>'Round off' and ap.payment_type='inbound' and aj.company_id = %s
                                                                			 and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
                                                                			 ::date between %s and %s
                                                                			 )

                                                                			 group by a.pos_config_ids,apr.amount)k

            '''

            self.env.cr.execute(re5, (
                                      company_id,config_id,date_start,date_end,
                                      company_id,date_start,date_end
                                      ))
            for row4 in self.env.cr.dictfetchall():
                # am6 = (row1['amount'] if row1['amount'] else 0)
                am3=(row1['amount'] if row1['amount'] else 0)
                if row4['amount']==None:
                    am3=0
                # am3 = (row4['amount'] if row4['amount'] else 0)
                # cr = (row['bank'] if row['bank'] else 0.0)

                # if config_id == coun_id:
                #     cr += (row['bank'] if row['bank'] else 0.0)
                # else:
                #     cr = 0

                # for i in pos_config_ids:
            # am8=am7+am2+am3


        res = {
            'card': am1+am2+am3,
        }

        # lines.append(res)

        if res:
            return res
        else:
            return []

    # def get_total_session(self,data, config_id):
    #     lines = []
    #     date_start = data['form']['date_start']
    #     date_end = data['form']['date_end']
    #     company_id = data['form']['company_id']
    #     counter_only = data['form']['counter_only']

    @api.model
    def render_html(self, docids, data=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        pos_config_ids = data['form']['pos_config_ids']
        config = self.env['pos.config'].browse(pos_config_ids)
        counter_only = data['form']['counter_only']
        header = False

        config.sorted(key=lambda r: r.id)
        count_of_config = 0
        # if counter_only:
        #     count_of_config =len(pos_config_ids)
        # if count_of_config ==1:
        #     header=self.env['pos.config'].browse(pos_config_ids).receipt_header

        valueone = 0
        valuetwo = 0
        valuethree = 0
        valuefour = 0
        valuefive = 0
        valuesix = 0

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        rescash = {}
        rescard = {}
        rescashline = []
        rescardline = []
        rescreditline = []
        total_session = []

        if not counter_only:
            valueone = self.get_cash(data)
            valuetwo = self.get_card(data)
            valuethree = self.get_credit(data)

        if counter_only and pos_config_ids:

            valuethree = self.get_credit(data)
            for pfg in config:
                cash = self.get_cash_wise(data, pfg.id)
                card = self.get_card_wise(data, pfg.id)
                credit = self.get_credit_so(data, pfg.id)
                total = cash['cash'] + card['card']
                total_session.append(total)
                rescashline.append(self.get_cash_wise(data, pfg.id))
                rescardline.append(self.get_card_wise(data, pfg.id))
                rescreditline.append(self.get_credit_so(data, pfg.id))
                # rescreditline.append(self.get_card_so(data, pfg.id))
                # total_session.append(self.get_credit_so(data, pfg.id))

        valuefour = rescashline

        valuefive = rescardline

        valuesix = rescreditline
        total_session_wise = total_session

        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start,
            'date_end': date_object_date_end,
            'data': data['form'],
            'pos_config_ids': pos_config_ids,
            'config': config,
            'time': time,
            'valueone': valueone,
            'valuetwo': valuetwo,
            'valuethree': valuethree,
            'counter_only': counter_only,
            'valuefour': valuefour,
            'valuefive': valuefive,
            'valuesix': valuesix,
            'total_session_wise': total_session_wise,
            'config_count': count_of_config,
            'header': header
        }

        return self.env['report'].render('qlty_salesreport_xls.qlty_salesreport_pdf', docargs)
