from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from odoo.tools.translate import _


class QltySaleDetailed(ReportXlsx):



    def get_cash(self, data):
        lines = []



        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']



        if counter_only:
            cash = 0
            sessions_ids = self.env['pos.session'].search([

                ('config_id', 'in', pos_config_ids)])
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start),('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done']),('session_id', 'in', sessions_ids.ids)])

            for order in pos_order:
                pos_account=self.env['account.bank.statement.line'].search([('id','in',order.statement_ids.ids)])
                for account in pos_account:
                    if account.journal_id.type=='cash':
                        cash+=account.amount

        else:

            cash = 0
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start),('date_order', '<=', date_end),
                ('company_id', '=', company_id),('state', 'in', ['paid','invoiced','done'])])
            account_invoice = self.env['account.invoice'].search(
                [('date_invoice', '>=', date_start), ('date_invoice', '<=', date_end),
                ('company_id', '=', company_id),
                ('state', 'in', ['paid', 'open']),('type', '=', 'out_invoice')])
            for invoice in account_invoice:
                for i in invoice.payment_move_line_ids:
                    account_move_line = self.env['account.move.line'].search([('id', '=', i.id),('journal_id.type', '=', 'cash'),('move_id.state', '=', 'posted')])
                    for j in account_move_line:
                        cash+=j.credit

            for order in pos_order:
                pos_account=self.env['account.bank.statement.line'].search([('id','in',order.statement_ids.ids)])
                for account in pos_account:
                    if account.journal_id.type=='cash':
                        cash+=account.amount


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
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']

        if counter_only:
            card = 0
            sessions_ids = self.env['pos.session'].search([

                ('config_id', 'in', pos_config_ids)])
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start),('date_order', '<=', date_end),
                ('company_id', '=', company_id),
                ('state', 'in', ['paid', 'invoiced', 'done']), ('session_id', 'in', sessions_ids.ids)])

            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])
                for account in pos_account:
                    if account.journal_id.type == 'bank':
                        card += account.amount

        else:

            card = 0
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start), ('date_order', '<=', date_end),
                                                  ('company_id', '=', company_id),
                                                  ('state', 'in', ['paid', 'invoiced','done'])])
            for order in pos_order:
                pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])
                for account in pos_account:
                    if account.journal_id.type == 'bank':
                        card += account.amount
            account_invoice = self.env['account.invoice'].search(
                [('date_invoice', '>=', date_start), ('date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('state', 'in', ['paid', 'open']),('type', '=', 'out_invoice')])
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
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_ids = data['form']['pos_config_ids']
        credit = 0
        if counter_only:
            credit = 0

        else:


            invoice = self.env['account.invoice'].search([('date_invoice', '>=', date_start), ('date_invoice', '<=', date_end),
                                                  ('company_id', '=', company_id),
                                                  ('state', 'in', ['draft', 'open']),('type', '=', 'out_invoice')])
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

    # def get_credit_pos(self, data,config_id):
    #     lines = []
    #
    #
    #
    #     date_start = data['form']['date_start']
    #     date_end = data['form']['date_end']
    #     company_id = data['form']['company_id']
    #     counter_only = data['form']['counter_only']
    #     pos_config_ids = data['form']['pos_config_ids']
    #
    #     credit = 0
    #
    #
    #
    #     if counter_only:
    #
    #         sessions_ids = self.env['pos.session'].search([
    #
    #             ('config_id', '=', config_id)])
    #         pos_order = self.env['pos.order'].search([('date_order', '>=', date_start),('date_order', '<=', date_end),
    #                                                   ('company_id', '=', company_id),
    #                                                   ('state', 'in', ['paid', 'invoiced', 'done']),('session_id', 'in', sessions_ids.ids)])
    #
    #         st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', pos_order.ids)]).ids
    #         if st_line_ids:
    #             self.env.cr.execute("""
    #                         SELECT COALESCE(sum(amount),'0') total
    #             FROM account_bank_statement_line AS absl,
    #                  account_bank_statement AS abs,
    #                  account_journal AS aj
    #             WHERE absl.statement_id = abs.id
    #                 AND abs.journal_id = aj.id and aj.type ='cash'
    #                  and aj.debt = 'true'
    #                 AND absl.id IN %s
    #                     """, (tuple(st_line_ids),))
    #             credit = self.env.cr.dictfetchall()
    #         else:
    #             credit = [{'total': 0.0}]
    #
    #         # for order in pos_order:
    #         #     pos_account=self.env['account.bank.statement.line'].search([('id','in',order.statement_ids.ids)])
    #         #     for account in pos_account:
    #         #         if account.journal_id.type=='cash':
    #         #             cash+=account.amount
    #
    #
    #     res = {
    #         'credit': credit[0]['total'] if credit else 0.0,
    #         }
    #
    #     lines.append(res)
    #
    #     if lines:
    #         return lines
    #     else:
    #         return []

    def get_cash_wise(self, data,config_id):
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
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start),('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'invoiced', 'done']),('session_id', 'in', sessions_ids.ids)])

            st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', pos_order.ids)]).ids
            if st_line_ids:
                self.env.cr.execute("""
                            SELECT COALESCE(sum(amount),'0') total
                FROM account_bank_statement_line AS absl,
                     account_bank_statement AS abs,
                     account_journal AS aj 
                WHERE absl.statement_id = abs.id
                    AND abs.journal_id = aj.id and aj.type ='cash'
                    AND absl.id IN %s 
                        """, (tuple(st_line_ids),))
                cash = self.env.cr.dictfetchall()
            else:
                cash = [{'total': 0.0}]

            # for order in pos_order:
            #     pos_account=self.env['account.bank.statement.line'].search([('id','in',order.statement_ids.ids)])
            #     for account in pos_account:
            #         if account.journal_id.type=='cash':
            #             cash+=account.amount


        res = {
            'cash': cash[0]['total'] if cash else 0.0,
            }

        lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_card_wise(self, data,config_id):


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
            pos_order = self.env['pos.order'].search([('date_order', '>=', date_start),('date_order', '<=', date_end),
                ('company_id', '=', company_id),
                ('state', 'in', ['paid', 'invoiced', 'done']), ('session_id', 'in', sessions_ids.ids)])

            # for order in pos_order:
            #     pos_account = self.env['account.bank.statement.line'].search([('id', 'in', order.statement_ids.ids)])
            #     for account in pos_account:
            #         if account.journal_id.type == 'bank':
            #             card += account.amount
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
                                 
                                AND absl.id IN %s 
                                    """, (tuple(st_line_ids),))
                card = self.env.cr.dictfetchall()
            else:
                card = [{'total': 0.0}]

        res = {
            'card': card[0]['total'] if card else 0.0,
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

        date_start = data['form']['date_start']

        date_end = data['form']['date_end']

        pos_config_ids = data['form']['pos_config_ids']

        counter_only = data['form']['counter_only']

        # category_id = data['form']['category_id']
        #
        # user_name = self.env["pos.session"].browse(session_id).user_id.name
        # session_name = self.env["pos.session"].browse(session_id).name

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

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        # sheet.write('A4' "Card", blue_mark)
        # sheet.write('A6', "Credit", blue_mark)


        if counter_only and pos_config_ids:
            sheet.merge_range('A1:B1', "Detailed Sales Report Session Wise ", blue_mark)
            sheet.write('A4', "Cash", blue_mark)
            sheet.merge_range('D1:E1', date_start + ' - ' + date_end, format1)
            sheet.write('C1', "Date :-", orange_mark)
            sheet.write('A6', "Card", blue_mark)
            # sheet.write('A8', "Credit", blue_mark)

            line_column = 1

            config = self.env['pos.config'].browse(pos_config_ids)
            for pfg in config:

                # line_column =
                #


                line_row = 3
                sheet.write(2, line_column, str(pfg.name), font_size_8)

                for line in self.get_cash_wise(data,pfg.id):
                    sheet.write(line_row, line_column, line['cash'], font_size_8)
                    line_row = line_row + 1
                #     line_column = 0
                # sheet.write(line_row, line_column, "Card", blue_mark)
                line_row = line_row + 1
                # line_column = 1
                for line in self.get_card_wise(data,pfg.id):
                    sheet.write(line_row, line_column, line['card'], font_size_8)
                    line_row = line_row + 1
                #     line_column = 0
                # sheet.write(line_row, line_column, "Credit", blue_mark)
                line_row = line_row + 1
                # line_column = 1
                # for line in self.get_credit_pos(data,pfg.id):
                #     sheet.write(line_row, line_column, line['credit'], font_size_8)
                #     line_row = line_row + 1
                    # line_column = 0
                line_column += 1
                total_cell_range = xl_range(3, line_column-1, line_row-1, line_column - 1)
                sheet.write_formula(line_row, line_column-1, '=SUM(' + total_cell_range + ')', format2)
            sheet.write(2, line_column,"Total", font_size_8)
            total_cell_range = xl_range(3, 1, 3, line_column-1)
            total_cell_range1 = xl_range(5, 1, 5, line_column-1)
            total_cell_range2 = xl_range(7, 1, 7, line_column-1)
            sheet.write_formula(3, line_column, '=SUM(' + total_cell_range + ')', format2)
            sheet.write_formula(5, line_column, '=SUM(' + total_cell_range1 + ')', format2)
            sheet.write_formula(7, line_column, '=SUM(' + total_cell_range2 + ')', format2)

            sheet.write('A13', "B2B Credit", blue_mark)
            for line in self.get_credit(data):
                sheet.write('B13', line['credit'], font_size_8)






        else:

            sheet.merge_range('A1:B1', "Detailed Sales Report ", format1)
            sheet.write('C1', "DATE :-", format1)
            sheet.merge_range('D1:E1', date_start + ' - ' + date_end, format1)

            sheet.write('A3', "Cash", blue_mark)
            line_row = 3

            line_column = 1
            for line in self.get_cash(data):
                sheet.write(line_row-1, line_column, line['cash'], font_size_8)
                line_row = line_row + 1
                line_column = 0
            sheet.write(line_row, line_column, "Card", blue_mark)
            line_row = line_row + 1
            line_column = 1
            for line in self.get_card(data):
                sheet.write(line_row-1, line_column, line['card'], font_size_8)
                line_row = line_row + 1
                line_column = 0
            # sheet.write(line_row, line_column, "Credit", blue_mark)
            # line_row = line_row + 1
            # line_column = 1
            # for line in self.get_credit(data):
            #     sheet.write(line_row, line_column, line['credit'], font_size_8)
            #     line_row = line_row + 1
            #     line_column = 0
            # sheet.write(line_row, line_column, "Income", blue_mark)
            # line_row = line_row + 1
            # line_column = 1
            # for line in self.get_credit(data):
            #     sheet.write(line_row, line_column, line['credit'], font_size_8)
            #     line_row = line_row + 1
            #     line_column = 0

            sheet.write(line_row, 0, "TOTAL", format1)

            total_cell_range = xl_range(3, 1, line_row - 1, 1)
            sheet.write_formula(line_row, 1, '=SUM(' + total_cell_range + ')', format2)





        # line_row = 3
        #
        # line_column = 1
        # for line in self.get_cash(data):
        #     sheet.write(line_row, line_column, line['cash'], font_size_8)
        #     line_row = line_row + 1
        #     line_column = 0
        # sheet.write(line_row, line_column, "Card", blue_mark)
        # line_row = line_row+1
        # line_column = 1
        # for line in self.get_card(data):
        #     sheet.write(line_row, line_column, line['card'], font_size_8)
        #     line_row = line_row + 1
        #     line_column = 0
        # sheet.write(line_row, line_column, "Credit", blue_mark)
        # line_row = line_row + 1
        # line_column = 1
        # for line in self.get_credit(data):
        #     sheet.write(line_row, line_column, line['credit'], font_size_8)
        #     line_row = line_row + 1
        #     line_column = 0
        # sheet.write(line_row, line_column, "Income", blue_mark)
        # line_row = line_row + 1
        # line_column = 1
        # for line in self.get_credit(data):
        #     sheet.write(line_row, line_column, line['credit'], font_size_8)
        #     line_row = line_row + 1
        #     line_column = 0

        # sheet.write(line_row, 0, "TOTAL", format1)
        #
        # total_cell_range = xl_range(3, 1, line_row - 1, 1)

        # total_cell_range_two = xl_range(3, 9, linw_row - 1, 9)
        # total_cell_range_three = xl_range(3, 10, linw_row - 1, 10)
        # total_cell_range_four = xl_range(3, 11, linw_row - 1, 11)
        # total_cell_range11 = xl_range(3, 12, linw_row - 1, 12)
        # total_cell_range13 = xl_range(3, 13, linw_row - 1, 13)
        # total_cell_range14 = xl_range(3, 14, linw_row - 1, 14)
        # total_cell_range15 = xl_range(3, 15, linw_row - 1, 15)
        # total_cell_range16 = xl_range(3, 16, linw_row - 1, 16)
        # total_cell_range17 = xl_range(3, 17, linw_row - 1, 17)
        # total_cell_range18 = xl_range(3, 18, linw_row - 1, 18)
        # total_cell_range19 = xl_range(3, 19, linw_row - 1, 19)
        # total_cell_range20 = xl_range(3, 20, linw_row - 1, 20)
        # total_cell_range21 = xl_range(3, 21, linw_row - 1, 21)
        # total_cell_range22 = xl_range(3, 22, linw_row - 1, 22)
        # total_cell_range23 = xl_range(3, 23, linw_row - 1, 23)


        # sheet.write_formula(line_row, 1, '=SUM(' + total_cell_range + ')', format1)




QltySaleDetailed('report.qlty_salesreport_xls.qlty_sale_xls.xlsx', 'sale.order')
