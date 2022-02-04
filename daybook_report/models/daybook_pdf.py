# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Reportdaybook(models.AbstractModel):
    _name = 'report.daybook_report.daybook_report_pdf'

    def get_opening(self, data):


        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']

        query = '''select sum(aml.balance) as open FROM account_move_line aml
            LEFT JOIN account_move am ON aml.move_id =am.id
            LEFT JOIN account_journal aj ON aj.id=aml.journal_id
            LEFT JOIN account_account_type aat ON aat.id = aml.user_type_id
            WHERE aj.type IN ('bank','cash') AND aat.name != 'Bank and Cash' AND aml.company_id = %s 
            AND am.date < %s AND am.state IN ('posted')'''

        self.env.cr.execute(query, (company_id,date_start))
        for row in self.env.cr.dictfetchall():
            value = row['open']

        if not value:
            value = 0

        return value

    def get_lines(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']

        query = ''' 
            SELECT date,voucher,particular,account,debit,credit FROM 
                (SELECT aml.date,am.name as voucher,CONCAT(aa.code, ' ', aa.name) AS account,aml.name as particular,aml.debit,aml.credit
                FROM account_move_line aml
                LEFT JOIN account_move am ON aml.move_id =am.id
                LEFT JOIN account_account aa ON aa.id = aml.account_id 
                LEFT JOIN account_journal aj ON aj.id=aml.journal_id
                LEFT JOIN account_account_type aat ON aat.id = aml.user_type_id
                WHERE aj.type IN ('bank','cash') AND aat.name != 'Bank and Cash' AND aml.company_id = %s 
                AND aml.date BETWEEN %s AND %s) as foo
            UNION ALL
            SELECT date,voucher,particular,account,debit,credit FROM 
                (select am.date,am.name as voucher,rp.name as particular,aj.name as account,
                CASE
                    WHEN am.amount is not null THEN am.amount
                    ELSE 0
                END as debit,
                CASE
                    WHEN am.amount is not null THEN am.amount
                    ELSE 0
                END as credit 
                from account_move am 
                left join account_journal aj on aj.id = am.journal_id
                left join res_partner  rp on rp.id = am.partner_id
                where am.company_id = %s  and am.date  BETWEEN %s AND  %s and aj.type='purchase') as boo
            ORDER BY date; '''
        self.env.cr.execute(query, (company_id, date_start, date_end,company_id, date_start, date_end))
        for row in self.env.cr.dictfetchall():
            date = datetime.strptime(row['date'], '%Y-%m-%d').date()
            res = {

                'date': date.strftime('%d-%m-%Y'),
                'voucher': row['voucher'] if row['voucher'] else " ",
                'account': row['account'] if row['account'] else " ",
                'particular':row['particular'] if row['particular'] else " ",
                'debit': row['debit'],
                'credit': row['credit'],
            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    def get_bank_and_cash_account(self,data):

        lines = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        query = ''' SELECT sum(aml.balance) as balance,aa.id,aa.name,aa.code FROM account_move_line aml
            LEFT JOIN account_account aa ON aa.id=aml.account_id
            LEFT JOIN account_move am ON aml.move_id =am.id
            WHERE aml.user_type_id = 3 AND am.date <= %s AND aml.company_id = %s
            GROUP BY aml.account_id,aa.id '''
        self.env.cr.execute(query, (date_end,company_id))
        for row in self.env.cr.dictfetchall():

            res = {
                'code': row['code'] if row['code'] else " ",
                'name': row['name'] if row['name'] else " ",
                'balance': row['balance'] if row['balance'] else 0,

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
        opening_bal = self.get_opening(data)
        details = self.get_lines(data)

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        bank_cash_act = self.get_bank_and_cash_account(data)

        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'date_end': date_object_date_end.strftime('%d-%m-%Y'),
            'data': data['form'],
            'details':details,
            'opening_bal': opening_bal,
            'bank_cash_act':bank_cash_act,

        }

        return self.env['report'].render('daybook_report.daybook_report_pdf', docargs)
