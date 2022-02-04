# -*- coding: utf-8 -*-

from datetime import datetime
import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ReportPartnerLedger123(models.AbstractModel):
    _name = 'report.report_partner_ledger.report_partnerledger1'

    def _lines(self,data,partner_ids):

        full_partner = []
        account_res = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['used_context']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '

        for partner in partner_ids :
            full_account = []
            params = [partner, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
            query = """
                SELECT "account_move_line".id,rp.name as partner_name, "account_move_line".date, j.code,j.name as ajname,cp.check_number as check_number,acc.code as a_code, acc.name as a_name, "account_move_line".ref, split_part(m.name, '/', 3) as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
                FROM """ + query_get_data[0] + """
                LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
                LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
                LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
                LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
                LEFT JOIN cheque_payment cp on (cp.id="account_move_line".cheque_payment_id)
                inner join res_partner rp on("account_move_line".partner_id = rp.id)
                WHERE "account_move_line".partner_id = %s
                    AND m.state IN %s
                    AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                    ORDER BY "account_move_line".date"""
            self.env.cr.execute(query, tuple(params))
            res = self.env.cr.dictfetchall()
            sum = 0.0
            debit = 0.0
            credit = 0.0
            lang_code = self.env.context.get('lang') or 'en_US'
            lang = self.env['res.lang']
            lang_id = lang._lang_get(lang_code)
            date_format = lang_id.date_format
            if res :
                for r in res:
                    r['date'] = datetime.strptime(r['date'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                    r['displayed_name'] = '-'.join(
                        r[field_name] for field_name in ('move_name', 'ref', 'name')
                        if r[field_name] not in (None, '', '/')
                    )
                    sum += r['debit'] - r['credit']
                    debit += r['debit']
                    credit += r['credit']
                    partner_name =r['partner_name']
                    r['progress'] = sum
                    r['currency_id'] = currency.browse(r.get('currency_id'))
                    full_account.append(r)
                sql="""SELECT  ml.partner_id,SUM(ml.debit) AS debit,SUM(ml.credit) AS credit,SUM(ml.balance) AS balance
                        FROM account_move_line ml  inner join account_move m on ml.move_id = m.id
                        where  ml.partner_id = %s and  ml.account_id IN %s and ml.date < %s and
                        (m.state = %s) GROUP BY ml.partner_id"""
                # para =[partner]+ data['computed']['account_ids'] + query_get_data[2][1]  + query_get_data[2][2]
                self.env.cr.execute(sql,[partner,tuple(data['computed']['account_ids']),query_get_data[2][1],query_get_data[2][2]] )
                res1 = self.env.cr.dictfetchall()

                result = dict((fn, 0.0) for fn in ['credit', 'debit','partner_name','balance'])
                result['debit']=debit
                result['credit'] = credit
                result['partner_name'] = partner_name
                result['balance'] = debit - credit
                result['lines'] = full_account
                result['opening'] = res1
                account_res.append(result)
        return account_res

    def _prepare_report_aged_partner_balance(self,data):
        # self.ensure_one()
        return {
            'date_at': data['form']['date_to'],
            'only_posted_moves': data['computed']['move_state'],
            'company_id':  data['form']['company_id'],
            'filter_account_ids': [(6, 0, data['computed']['account_ids'])],
            'filter_partner_ids': [(6, 0, data['form']['partner_ids'])],
            'show_move_line_details': data['form']['show_move_line_details'],
        }

    @api.multi
    def print_report(self):
        report_name = 'report_partner_ledger.report_aged_partner_balance_qweb'
        return self.env['report'].get_action(docids=self.ids,report_name=report_name)
    def _export(self,data):
        """Default export is PDF."""
        model = self.env['report_aged_partner_balance_qweb']
        report = model.create(self._prepare_report_aged_partner_balance(data))
        report.compute_data_for_report()
        return report

    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        data['computed'] = {}

        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        data['computed']['ACCOUNT_TYPE'] =  ['payable', 'receivable']
        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.internal_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]

        reconcile_clause = "" if data['form']['used_context']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '

        partner_ids =  data['form']['partner_ids']
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref, x.name))

        # partners_name = []
        pars = self.env['res.partner'].search([('id', 'in', partner_ids)])
        partners_name = [par.name for par in pars]
        # exp = self._export(data)
        model = self.env['report_aged_partner_balance_qweb']
        report = model.create(self._prepare_report_aged_partner_balance(data))
        report.compute_data_for_report()
        partners_res = self._lines(data,partner_ids)
        docargs = {
            'doc_ids': partner_ids,
            'doc_model': self.env['res.partner'],
            'data': data['form'],
            'docs': partners,
            'time': time,
            'partners_res': partners_res,
            'print_partnersname': partners_name,
            'report' : report
        }
        return  self.env['report'].render('report_partner_ledger.report_partnerledger1', docargs)
