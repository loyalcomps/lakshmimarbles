from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from odoo.tools.translate import _


class ConsolidatedXls(ReportXlsx):

    def get_all_branch(self,data,stock_loc):
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']
        opening_balance = 0
        closing_balance = 0
        cash = 0
        card =0
        credit =0
        total =0
        opening_query = '''
            select sum(balance_start) as open_balance from account_bank_statement where pos_session_id in
            (select id from pos_session where config_id in (select id from pos_config where stock_location_id = %s and company_id = %s)
            and to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date = %s
            and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date = %s)
            and cashbox_start_id is not null
        '''
        self.env.cr.execute(opening_query, (stock_loc,company_id,date_start,date_start))
        for row in self.env.cr.dictfetchall():
            opening_balance += row['open_balance'] if row['open_balance'] else 0

        closing_query = '''
                    select sum(balance_end_real) as close_balance from account_bank_statement where pos_session_id in
                    (select id from pos_session where config_id in (select id from pos_config where stock_location_id = %s and company_id = %s)
                    and to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date = %s
                    and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date = %s)
                    and cashbox_end_id is not null
                        '''
        self.env.cr.execute(closing_query, (stock_loc,company_id,date_start,date_start))
        for row in self.env.cr.dictfetchall():
            closing_balance += row['close_balance'] if row['close_balance'] else 0

        pos_cb_query = '''
            select sum (absl.amount) as amount,aj.type from account_bank_statement_line as absl
            left join account_journal as aj on aj.id =  absl.journal_id
            where absl.pos_statement_id in (select id from pos_order where session_id in
            (select id from pos_session where config_id in (select id from pos_config where stock_location_id = %s and company_id = %s)
            and to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date = %s
            and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date = %s)
            ) and aj.used_for_rounding is not true
            group by aj.type
        '''
        self.env.cr.execute(pos_cb_query, (stock_loc,company_id,date_start,date_start))
        for row in self.env.cr.dictfetchall():
            cash += row['amount'] if row['type']=='cash' else 0
            card += row['amount'] if row['type'] == 'bank' else 0
        payment_cash = '''
            select sum(ap.amount) as payment_amount from account_payment as ap
            left join account_journal as aj on(aj.id=ap.journal_id)
            left join pos_session as ps on(ps.id=ap.pos_counter_ids)
            left join pos_config as pc on pc.id=ps.config_id
            where aj.type='cash' and aj.used_for_rounding is not true and ap.state!='draft' and ap.payment_type='inbound' and aj.company_id = %s
            and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
            ::date between %s and %s and pc.stock_location_id =%s
                '''
        self.env.cr.execute(payment_cash, (company_id,date_start,date_start,stock_loc,))
        for row in self.env.cr.dictfetchall():
            cash += row['payment_amount'] if row['payment_amount'] else 0

        payment_bank = '''
                    select sum(ap.amount) as payment_amount from account_payment as ap
                    left join account_journal as aj on(aj.id=ap.journal_id)
                    left join pos_session as ps on(ps.id=ap.pos_counter_ids)
            left join pos_config as pc on pc.id=ps.config_id
                    where aj.type='bank' and aj.used_for_rounding is not true and ap.state!='draft' and ap.payment_type='inbound' and aj.company_id = %s
                    and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
                    ::date between %s and %s and pc.stock_location_id =%s
                        '''
        self.env.cr.execute(payment_bank, (company_id, date_start, date_start, stock_loc,))
        for row in self.env.cr.dictfetchall():
            card += row['payment_amount'] if row['payment_amount'] else 0


        pos_credit_query = '''
            select sum(ai.amount_total) as credit from account_invoice as ai
            left join pos_order as po on po.invoice_id = ai.id
            where ai.id in(
            select invoice_id from pos_order where session_id in
            (select id from pos_session where config_id in (select id from pos_config where stock_location_id = %s and company_id = %s)
            and to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date = %s
            and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date = %s) and invoice_remark is not null
            ) and ai.partial_payment_remark is not null
            and po.invoice_remark is not null
            and (po.id not in(select pos_statement_id from account_bank_statement_line where pos_statement_id is not null))
                '''
        self.env.cr.execute(pos_credit_query, (stock_loc,company_id,date_start,date_start))
        for row in self.env.cr.dictfetchall():
            credit += row['credit'] if row['credit'] else 0

        pos_credit_query2 = '''
                    select (sum(ai.amount_total)-(select sum(amount) from account_bank_statement_line where pos_statement_id = po.id)) as credit,po.id from account_invoice as ai
            left join pos_order as po on po.invoice_id = ai.id
            where ai.id in(select invoice_id from pos_order where session_id in
            (select id from pos_session where config_id in (select id from pos_config where stock_location_id = %s and company_id = %s)
            and to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date = %s
            and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date = %s) and invoice_remark is not null
            ) and ai.partial_payment_remark is not null
            and po.invoice_remark is not null
            and ai.amount_total != (select sum(amount) from account_bank_statement_line where pos_statement_id = po.id)
            group by po.id
                        '''
        self.env.cr.execute(pos_credit_query2, (stock_loc, company_id, date_start, date_start))
        for row in self.env.cr.dictfetchall():
            credit += row['credit'] if row['credit'] else 0

        total =total+opening_balance+cash+card+credit
        location = self.env['stock.location'].browse(stock_loc)
        for record in location:
            if record.location_id:
                name = record.location_id.name+"/"+record.name
            else:
                name = record.name
        res = {
            'open':opening_balance,
            'cash':cash,
            'card':card,
            'credit':credit,
            'close':closing_balance,
            'total':total,
            'location':name,
        }

        if res:
            return res
        else:
            return False

    def get_session_wise(self,data,session):

        date_start = data['form']['date_start']
        company_id = data['form']['company_id']
        opening_balance = 0
        closing_balance = 0
        cash = 0
        card = 0
        credit = 0
        total = 0
        excess = 0
        opening_query = '''
                    select sum(balance_start) as open_balance from account_bank_statement where pos_session_id = %s and company_id = %s
                    and cashbox_start_id is not null'''
        self.env.cr.execute(opening_query, (session,company_id))
        for row in self.env.cr.dictfetchall():
            opening_balance += row['open_balance'] if row['open_balance'] else 0

        closing_query = '''
                    select sum(balance_end_real) as close_balance from account_bank_statement where pos_session_id = %s and company_id = %s
                    and cashbox_end_id is not null
                        '''
        self.env.cr.execute(closing_query, (session,company_id))
        for row in self.env.cr.dictfetchall():
            closing_balance += row['close_balance'] if row['close_balance'] else 0

        pos_cb_query = '''
            select sum (absl.amount) as amount,aj.type from account_bank_statement_line as absl
            left join account_journal as aj on aj.id =  absl.journal_id
            where absl.pos_statement_id in (select id from pos_order where session_id = %s and company_id = %s)
            and aj.used_for_rounding is not true
            group by aj.type
        '''
        self.env.cr.execute(pos_cb_query, (session,company_id))
        for row in self.env.cr.dictfetchall():
            cash += row['amount'] if row['type']=='cash' else 0
            card += row['amount'] if row['type'] == 'bank' else 0
        payment_cash = '''
            select sum(ap.amount) as payment_amount from account_payment as ap
            left join account_journal as aj on(aj.id=ap.journal_id)
            left join pos_session as ps on(ps.id=ap.pos_counter_ids)
            where aj.type='cash' and aj.used_for_rounding is not true and ap.state!='draft' and ap.payment_type='inbound' and aj.company_id = %s
            and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
            ::date between %s and %s and ps.id =%s
                '''
        self.env.cr.execute(payment_cash, (company_id,date_start,date_start,session,))
        for row in self.env.cr.dictfetchall():
            cash += row['payment_amount'] if row['payment_amount'] else 0

        payment_bank = '''
                    select sum(ap.amount) as payment_amount from account_payment as ap
            left join account_journal as aj on(aj.id=ap.journal_id)
            left join pos_session as ps on(ps.id=ap.pos_counter_ids)
            where aj.type='bank' and aj.used_for_rounding is not true and ap.state!='draft' and ap.payment_type='inbound' and aj.company_id = %s
            and  to_char(date_trunc('day',ap.payment_date),'YYYY-MM-DD')
            ::date between %s and %s and ps.id =%s
                        '''
        self.env.cr.execute(payment_bank, (company_id, date_start, date_start, session,))
        for row in self.env.cr.dictfetchall():
            card += row['payment_amount'] if row['payment_amount'] else 0


        pos_credit_query = '''
            select sum(amount_total) as credit from account_invoice as ai
            left join pos_order as po on po.invoice_id = ai.id
            where ai.id in(
            select invoice_id from pos_order where session_id = %s and company_id = %s
             and invoice_remark is not null
            ) and ai.partial_payment_remark is not null
            and po.invoice_remark is not null
            and (po.id not in(select pos_statement_id from account_bank_statement_line where pos_statement_id is not null))

                '''
        self.env.cr.execute(pos_credit_query, (session,company_id))
        for row in self.env.cr.dictfetchall():
            credit += row['credit'] if row['credit'] else 0

        pos_credit_query2 = '''
            select (sum(ai.amount_total)-(select sum(amount) from account_bank_statement_line where pos_statement_id = po.id)) as credit,po.id from account_invoice as ai
            left join pos_order as po on po.invoice_id = ai.id
            where ai.id in(
            select invoice_id from pos_order where session_id = %s and company_id = %s
            and invoice_remark is not null
            ) and ai.partial_payment_remark is not null
            and po.invoice_remark is not null and
            (ai.amount_total != (select sum(amount) from account_bank_statement_line where pos_statement_id = po.id))
            group by po.id
            '''
        self.env.cr.execute(pos_credit_query2, (session, company_id))
        for row in self.env.cr.dictfetchall():
            credit += row['credit'] if row['credit'] else 0

        excess_query = '''
            select sum(amount) as loss from account_bank_statement_line as absl
            left join account_bank_statement as abs on absl.statement_id = abs.id
            where abs.pos_session_id = %s and absl.pos_statement_id is null and absl.company_id = %s
        '''
        self.env.cr.execute(excess_query, (session,company_id))
        for row in self.env.cr.dictfetchall():
            excess += row['loss'] if row['loss'] else 0

        total = total + opening_balance + cash + card + credit
        res = {
            'open': opening_balance,
            'cash': cash,
            'card': card,
            'credit': credit,
            'close': closing_balance,
            'total': total,
            'excess':excess,
        }

        if res:
            return res
        else:
            return False

    def get_denomination(self,data,config):
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']
        res = {.50:0,
               1:0,
               2:0,
               5:0,
               10:0,
               20:0,
               50:0,
               100:0,
               200:0,
               500:0,
               2000:0,}

        deno_query = '''
            select number,coin_value from account_cashbox_line where cashbox_id =(
            select cashbox_end_id from account_bank_statement where pos_session_id =(
            select id from pos_session where config_id = %s
            and to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date = %s
            and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date = %s  order by id desc limit 1)
            and cashbox_end_id is not null)
                '''
        self.env.cr.execute(deno_query, (config, date_start,date_start))
        for row in self.env.cr.dictfetchall():
            if row['coin_value'] in res:
                res[row['coin_value']] +=row['number']
            else:
                res[row['coin_value']] = row['number']

        if res:
            return res
        else:
            return False
    def total_denomination(self,data, stock_loc):
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']
        res = {.50: 0,
               1: 0,
               2: 0,
               5: 0,
               10: 0,
               20: 0,
               50: 0,
               100: 0,
               200: 0,
               500: 0,
               2000: 0, }

        deno_query = '''
            select sum(number) as total,coin_value from account_cashbox_line where cashbox_id in (
            select cashbox_end_id from account_bank_statement where pos_session_id in(
            select foo.session_id from(
            select max(id) as session_id,config_id from pos_session where config_id in (select id from pos_config where stock_location_id = %s)
            and to_char(date_trunc('day',pos_session.start_at),'YYYY-MM-DD')::date = %s
            and to_char(date_trunc('day',pos_session.stop_at),'YYYY-MM-DD')::date = %s  group by config_id) as foo)
            and cashbox_end_id is not null) group by coin_value
                        '''
        self.env.cr.execute(deno_query, (stock_loc, date_start, date_start))
        for row in self.env.cr.dictfetchall():
            if row['coin_value'] in res:
                res[row['coin_value']] += row['total']*row['coin_value']
            else:
                res[row['coin_value']] = row['total']*row['coin_value']

        if res:
            return res
        else:
            return False

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Consolidated Sale Report'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 25)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 10)
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

        date_start = data['form']['date_start']
        counter_only = data['form']['counter_only']
        company = self.env['res.company'].browse(data['form']['company_id']).name
        company_address = self.env['res.company'].browse(data['form']['company_id']).street

        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})
        column_style_0 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'bg_color': '#F5B7B1'})
        column_style_1 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bg_color': '#D2B4DE'})
        column_style_2 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bg_color': 'AED6F1'})
        column_style_3 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bg_color': '#A2D9CE'})
        column_style_4 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bg_color': '#ABEBC6'})
        column_style_5 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bg_color': '#FAD7A0'})
        column_style_6 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bg_color': '#F5CBA7'})
        column_style_7 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bg_color': '#DC7633'})
        row_total_style=workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True,})
        company_style = workbook.add_format(
            {'font_size': 20, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
             'bold': True,})
        address_style = workbook.add_format(
            {'font_size': 18, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
             'bold': True,})
        title_style = workbook.add_format({'font_size': 16, 'bold': True,

                                           'bottom': 1,})

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True,})
        format11 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center', 'bold': True})
        yellow_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': 'fcf22f','align': 'center'})
        orange_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': 'f4a442'})
        green_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': '32CD32'})
        blue_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             })
        bold = workbook.add_format({'bold': True})

        sheet.merge_range('A1:H1', company, company_style)
        sheet.merge_range('A2:H2', company_address, address_style)
        sheet.merge_range('A3:H3', "Consolidated Sale Report ", title_style)
        sheet.merge_range('A4:D4', "Report Date"+" :- "+ date_start,title_style)
        if counter_only:
            stock_loc = data['form']['stock_loc']
            location = self.env['stock.location'].browse(stock_loc)
            for record in location:
                if record.location_id:
                    name = record.location_id.name + "/" + record.name
                else:
                    name = record.name
            sheet.merge_range('E4:H4', "Branch/Stock Location : "+name, title_style)
            line_row = 5
            line_column = 0
            sheet.write(line_row, line_column, "Sl No", blue_mark)
            sheet.write(line_row, line_column + 1, "User Name", blue_mark)
            sheet.write(line_row, line_column + 2, "Payment", blue_mark)
            sheet.write(line_row, line_column + 3, "Session 1", blue_mark)
            sheet.write(line_row, line_column + 4, "Session 2", blue_mark)
            sheet.write(line_row, line_column + 5, "Session 3", blue_mark)
            sheet.write(line_row, line_column + 6, "Session 4", blue_mark)
            sheet.write(line_row, line_column + 7, "Total", blue_mark)

            line_row += 1
            line_column = 0

            sl =1
            pos_config_ids = self.env['pos.config'].search([('stock_location_id','=',stock_loc)])
            for config in pos_config_ids:
                sheet.write(line_row, line_column, "", format1)
                row = line_row
                column = line_column
                sheet.write(line_row, line_column+1, "", format1)
                sheet.write(line_row, line_column + 2, "Opening", font_size_8)
                sheet.write(line_row + 1, line_column + 2, "Cash", font_size_8)
                sheet.write(line_row + 2, line_column + 2, "Card", font_size_8)
                sheet.write(line_row + 3, line_column + 2, "Credit", font_size_8)
                sheet.write(line_row + 4, line_column + 2, "Total", font_size_8)
                sheet.write(line_row + 5, line_column + 2, "Closing", font_size_8)
                sheet.write(line_row + 6, line_column + 2, "Excess/ Short", font_size_8)
                sl_cell1 = xl_rowcol_to_cell(row+1, column)
                sl_cell2 = xl_rowcol_to_cell(row+5, column)
                sheet.merge_range(sl_cell1 + ':' + sl_cell2, sl, format1)

                user_cell1 = xl_rowcol_to_cell(row + 1, column+1)
                user_cell2 = xl_rowcol_to_cell(row + 5, column+1)
                sheet.merge_range(user_cell1 + ':' + user_cell2, config.name, format1)
                sheet.write(line_row+6, line_column, "", format1)
                sheet.write(line_row+6, line_column+1, "", format1)

                session_ids = self.env['pos.session'].search([('config_id','=',config.id),('start_at','>=',date_start),
                                                              ('stop_at','<=',date_start)],limit=4)
                session_column = 3
                no_count = session_column
                count = 0
                for session in session_ids:
                    count += 1
                    value = self.get_session_wise(data,session.id)
                    sheet.write(line_row, session_column, value["open"], font_size_8)
                    sheet.write(line_row + 1, session_column, value["cash"], font_size_8)
                    sheet.write(line_row + 2, session_column, value["card"], font_size_8)
                    sheet.write(line_row + 3, session_column, value["credit"], font_size_8)
                    sheet.write(line_row + 4, session_column, value["total"], font_size_8)
                    sheet.write(line_row + 5, session_column, value["close"], font_size_8)
                    sheet.write(line_row + 6, session_column, value["excess"], font_size_8)

                    session_column += 1
                    no_count=session_column
                if count != 4:
                    i = count
                    while i <=4:
                        sheet.write(line_row, no_count, 0, font_size_8)
                        sheet.write(line_row + 1, no_count, 0, font_size_8)
                        sheet.write(line_row + 2, no_count, 0, font_size_8)
                        sheet.write(line_row + 3, no_count, 0, font_size_8)
                        sheet.write(line_row + 4, no_count, 0, font_size_8)
                        sheet.write(line_row + 5, no_count, 0, font_size_8)
                        sheet.write(line_row + 6, no_count, 0, font_size_8)
                        i += 1
                        no_count += 1

                if session_ids:
                    open_range = xl_range(line_row, 3, line_row, 6)
                    cash_range = xl_range(line_row+1, 3, line_row+1, 6)
                    card_range = xl_range(line_row+2, 3, line_row+2, 6)
                    credit_range = xl_range(line_row+3, 3, line_row+3, 6)
                    total_range = xl_range(line_row+4, 3, line_row+4, 6)
                    close_range = xl_range(line_row+5, 3, line_row+5, 6)
                    excess_range = xl_range(line_row+6, 3, line_row+6, 6)
                    sheet.write_formula(line_row, 7, '=SUM(' + open_range + ')', format1)
                    sheet.write_formula(line_row+1, 7, '=SUM(' + cash_range + ')', format1)
                    sheet.write_formula(line_row+2, 7, '=SUM(' + card_range + ')', format1)
                    sheet.write_formula(line_row+3, 7, '=SUM(' + credit_range + ')', format1)
                    sheet.write_formula(line_row+4, 7, '=SUM(' + total_range + ')', format1)
                    sheet.write_formula(line_row+5, 7, '=SUM(' + close_range + ')', format1)
                    sheet.write_formula(line_row+6, 7, '=SUM(' + excess_range + ')', format1)

                line_row = line_row+7
                line_column = 0
                sl +=1
            grand_total_range = xl_range(6, 7, line_row-1, 7)
            gt_cell1 = xl_rowcol_to_cell(line_row, 0)
            gt_cell2 = xl_rowcol_to_cell(line_row, 6)
            sheet.merge_range(gt_cell1 + ':' + gt_cell2, "TOTAL", format1)
            sheet.write_formula(line_row, 7, '=SUM(' + grand_total_range + ')', format1)

            line_row +=3
            line_column = 0
            gt_cell1 = xl_rowcol_to_cell(line_row, 0)
            gt_cell2 = xl_rowcol_to_cell(line_row, 8)
            sheet.merge_range(gt_cell1 + ':' + gt_cell2, "Last Session of Each Counter -Denomination", title_style)
            # sheet.write(line_row, line_column, "Denomination", blue_mark)
            line_row += 1
            line_column = 0
            sheet.write(line_row, line_column, "Denomination", blue_mark)
            head_row =line_row
            sheet.write(line_row + 1, line_column, .50, column_style_0)
            sheet.write(line_row + 2, line_column, 1, column_style_1)
            sheet.write(line_row + 3, line_column, 2, column_style_2)
            sheet.write(line_row + 4, line_column, 5, column_style_3)
            sheet.write(line_row + 5, line_column, 10, column_style_4)
            sheet.write(line_row + 6, line_column, 20, column_style_5)
            sheet.write(line_row + 7, line_column, 50, column_style_6)
            sheet.write(line_row + 8, line_column, 100, column_style_7)
            sheet.write(line_row + 9, line_column, 200, column_style_0)
            sheet.write(line_row + 10, line_column, 500, column_style_1)
            sheet.write(line_row + 11, line_column, 2000, column_style_2)
            sheet.write(line_row + 12, line_column, "Total", font_size_8)
            line_column +=1
            line_row=head_row
            for config in pos_config_ids:
                sheet.write(line_row, line_column, config.name, blue_mark)
                sheet.write(line_row, line_column + 1, "Total", blue_mark)

                value = self.get_denomination(data, config.id)
                sheet.write(line_row + 1, line_column, value[.50], column_style_0)
                sheet.write(line_row + 2, line_column, value[1], column_style_1)
                sheet.write(line_row + 3, line_column, value[2], column_style_2)
                sheet.write(line_row + 4, line_column, value[5], column_style_3)
                sheet.write(line_row + 5, line_column, value[10], column_style_4)
                sheet.write(line_row + 6, line_column, value[20], column_style_5)
                sheet.write(line_row + 7, line_column, value[50], column_style_6)
                sheet.write(line_row + 8, line_column, value[100], column_style_7)
                sheet.write(line_row + 9, line_column, value[200], column_style_0)
                sheet.write(line_row + 10, line_column, value[500], column_style_1)
                sheet.write(line_row + 11, line_column, value[2000], column_style_2)
                grand_total_range = xl_range(line_row + 1, line_column, line_row +11, line_column)

                sheet.write_formula(line_row+ 12, line_column, '=SUM(' + grand_total_range + ')', format1)

                #total
                sheet.write(line_row + 1, line_column+1, value[.50]*.50, column_style_0)
                sheet.write(line_row + 2, line_column+1, value[1]*1, column_style_1)
                sheet.write(line_row + 3, line_column+1, value[2]*2, column_style_2)
                sheet.write(line_row + 4, line_column+1, value[5]*5, column_style_3)
                sheet.write(line_row + 5, line_column+1, value[10]*10, column_style_4)
                sheet.write(line_row + 6, line_column+1, value[20]*20, column_style_5)
                sheet.write(line_row + 7, line_column+1, value[50]*50, column_style_6)
                sheet.write(line_row + 8, line_column+1, value[100]*100, column_style_7)
                sheet.write(line_row + 9, line_column+1, value[200]*200, column_style_0)
                sheet.write(line_row + 10, line_column+1, value[500]*500, column_style_1)
                sheet.write(line_row + 11, line_column+1, value[2000]*2000, column_style_2)

                grand_total_range = xl_range(line_row + 1, line_column+1, line_row + 11, line_column+1)

                sheet.write_formula(line_row + 12, line_column+1, '=SUM(' + grand_total_range + ')', format1)

                line_column +=2
            sheet.write(line_row, line_column, "Grand Total", blue_mark)
            total_denom = self.total_denomination(data, stock_loc)
            sheet.write(line_row + 1, line_column, total_denom[.50], column_style_0)
            sheet.write(line_row + 2, line_column, total_denom[1], column_style_1)
            sheet.write(line_row + 3, line_column, total_denom[2], column_style_2)
            sheet.write(line_row + 4, line_column, total_denom[5], column_style_3)
            sheet.write(line_row + 5, line_column, total_denom[10], column_style_4)
            sheet.write(line_row + 6, line_column, total_denom[20], column_style_5)
            sheet.write(line_row + 7, line_column, total_denom[50], column_style_6)
            sheet.write(line_row + 8, line_column, total_denom[100], column_style_7)
            sheet.write(line_row + 9, line_column, total_denom[200], column_style_0)
            sheet.write(line_row + 10, line_column, total_denom[500], column_style_1)
            sheet.write(line_row + 11, line_column, total_denom[2000], column_style_2)
            grand_total_range = xl_range(line_row + 1, line_column, line_row + 11, line_column)

            sheet.write_formula(line_row + 12, line_column, '=SUM(' + grand_total_range + ')', format1)







        else:
            sheet.merge_range('E4:H4', "All Branch", title_style)
            stock_loc_ids = self.env['stock.location'].search([('usage','=','internal')])
            line_row = 4
            line_column =0
            sheet.write(line_row, line_column, "Sl No", blue_mark)
            sheet.write(line_row, line_column+1, "Branch", blue_mark)
            sheet.write(line_row, line_column+2, "Opening", blue_mark)
            sheet.write(line_row, line_column+3, "Cash", blue_mark)
            sheet.write(line_row, line_column+4, "Card", blue_mark)
            sheet.write(line_row, line_column+5, "Credit", blue_mark)
            sheet.write(line_row, line_column+6, "Total", blue_mark)
            sheet.write(line_row, line_column+7, "Closing", blue_mark)

            sl=1
            line_row += 1
            row = line_row
            line_column = 0
            for stock_loc in stock_loc_ids:
                value = self.get_all_branch(data, stock_loc.id)
                if value:
                    sheet.write(line_row, line_column, sl,column_style_0)
                    sheet.write(line_row, line_column+1, value['location'], column_style_1)
                    sheet.write(line_row, line_column + 2, value['open'], column_style_2)
                    sheet.write(line_row, line_column + 3, value['cash'], column_style_3)
                    sheet.write(line_row, line_column + 4, value['card'], column_style_4)
                    sheet.write(line_row, line_column + 5, value['credit'], column_style_5)
                    sheet.write(line_row, line_column + 6, value['total'], column_style_6)
                    sheet.write(line_row, line_column + 7, value['close'], column_style_7)

                    sl +=1
                    line_row = line_row + 1
                    line_column = 0
            cell1 = xl_rowcol_to_cell(line_row, 0)
            cell2 = xl_rowcol_to_cell(line_row, 1)
            sheet.merge_range(cell1+':'+cell2,"TOTAL", row_total_style)
            total_cell_range_1 = xl_range(row, 2, line_row - 1, 2)
            total_cell_range_2 = xl_range(row, 3, line_row - 1, 3)
            total_cell_range_3 = xl_range(row, 4, line_row - 1, 4)
            total_cell_range_4 = xl_range(row, 5, line_row - 1, 5)
            total_cell_range_5 = xl_range(row, 6, line_row - 1, 6)
            total_cell_range_6 = xl_range(row, 7, line_row - 1, 7)
            sheet.write_formula(line_row, 2, '=SUM(' + total_cell_range_1 + ')', row_total_style)
            sheet.write_formula(line_row, 3, '=SUM(' + total_cell_range_2 + ')', row_total_style)
            sheet.write_formula(line_row, 4, '=SUM(' + total_cell_range_3 + ')', row_total_style)
            sheet.write_formula(line_row, 5, '=SUM(' + total_cell_range_4 + ')', row_total_style)
            sheet.write_formula(line_row, 6, '=SUM(' + total_cell_range_5 + ')', row_total_style)
            sheet.write_formula(line_row, 7, '=SUM(' + total_cell_range_6 + ')', row_total_style)


ConsolidatedXls('report.consolidated_sale_report.consolidated_sale_xls.xlsx', 'account.move')
