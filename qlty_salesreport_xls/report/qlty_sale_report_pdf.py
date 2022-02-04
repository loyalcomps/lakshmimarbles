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
                    if account.journal_id.type == 'cash':
                        cash += account.amount

        else:

            cash = 0
            query1 = '''select invoice_id from pos_order where invoice_id is not null and company_id = %s and to_char(date_trunc('day',date_order),'YYYY-MM-DD')::date between %s and %s'''
            self.env.cr.execute(query1, (company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                invoice_id.append(row['invoice_id'])
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done'])])
            account_invoice = self.env['account.invoice'].search(
                [('date_invoice', '>=', date_start), ('date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('state', 'in', ['paid', 'open']), ('type', '=', 'out_invoice'),
                 ('id', 'not in', invoice_id)])
            for invoice in account_invoice:
                for i in invoice.payment_move_line_ids:
                    account_move_line = self.env['account.move.line'].search(
                        [('id', '=', i.id), ('journal_id.type', '=', 'cash'), ('move_id.state', '=', 'posted')])
                    for j in account_move_line:
                        cash += j.credit

            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])
                for account in pos_account:
                    if account.journal_id.type == 'cash':
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
        invoice_id = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
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
            query1 = '''select invoice_id from pos_order where invoice_id is not null and company_id = %s and to_char(date_trunc('day',date_order),'YYYY-MM-DD')::date between %s and %s'''
            self.env.cr.execute(query1, (company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                invoice_id.append(row['invoice_id'])
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
                 ('state', 'in', ['paid', 'open']), ('type', '=', 'out_invoice'),
                 ('id', 'in', invoice_id)])
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
        invoice_id = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        credit = 0
        if counter_only:
            query1 = '''select invoice_id from pos_order where invoice_id is not null and company_id = %s and to_char(date_trunc('day',date_order),'YYYY-MM-DD')::date between %s and %s'''
            self.env.cr.execute(query1, (company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                invoice_id.append(row['invoice_id'])
            credit = 0
            invoice = self.env['account.invoice'].search(
                [('date_invoice', '>=', date_start), ('date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('state', 'in', ['draft', 'open']), ('type', '=', 'out_invoice'),
                 ('id', 'not in', invoice_id)])
            for order in invoice:
                if order.state == 'draft':
                    credit += order.amount_total
                if order.state == 'open':
                    credit += order.residual

        else:
            query1 = '''select invoice_id from pos_order where invoice_id is not null and company_id = %s and to_char(date_trunc('day',date_order),'YYYY-MM-DD')::date between %s and %s'''
            self.env.cr.execute(query1, (company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                invoice_id.append(row['invoice_id'])

            invoice = self.env['account.invoice'].search(
                [('date_invoice', '>=', date_start), ('date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('state', 'in', ['draft', 'open']), ('type', '=', 'out_invoice'),
                 ('id', 'not in', invoice_id)])
            for order in invoice:
                if order.state == 'draft':
                    credit += order.amount_total
                if order.state == 'open':
                    credit += order.residual
        res = {
            'credit': credit,
        }

        lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_credit_so(self, data, config_id):
        lines = []
        invoice_id = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        credit = 0

        if counter_only:
            query1 = '''select invoice_id from pos_order where invoice_id is not null and company_id = %s and to_char(date_trunc('day',date_order),'YYYY-MM-DD')::date between %s and %s'''
            self.env.cr.execute(query1, (company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                invoice_id.append(row['invoice_id'])
                # config=self.env['pos.config'].search([('name','=','DESHABHIMANI')]).id
                # if config==config_id:
            credit = 0
            invoice = self.env['account.invoice'].search(
                    [('date_invoice', '>=', date_start), ('date_invoice', '<=', date_end),
                     ('company_id', '=', company_id),
                     ('state', 'in', ['draft', 'open']), ('type', '=', 'out_invoice'), ('id', 'not in', invoice_id)])
            for order in invoice:
                if order.state == 'draft':
                    credit += order.amount_total
                if order.state == 'open':
                    credit += order.residual

        res = {
            'credit': credit if credit else 0.0,
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
                    and aj.debt = 'true'
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

        cash = 0

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
                    and aj.debt != 'true'
                    AND absl.id IN %s 
                        """, (tuple(st_line_ids),))
                cash = self.env.cr.dictfetchall()
            else:
                cash = [{'total': 0.0}]

        res = {
            'cash': cash[0]['total'] if cash else 0.0,
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
        card = 0

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
                                AND abs.journal_id = aj.id and aj.type ='bank'
                                and aj.debt != 'true'
                                AND absl.id IN %s 
                                    """, (tuple(st_line_ids),))
                card = self.env.cr.dictfetchall()
            else:
                card = [{'total': 0.0}]

        res = {
            'card': card[0]['total'] if card else 0.0,
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
                # rescreditline.append(self.get_credit_so(data, pfg.id))
                rescreditline.append(self.get_card_so(data, pfg.id))
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
