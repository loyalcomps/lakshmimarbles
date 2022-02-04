from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _

from datetime import datetime

class qltydaybookXls(ReportXlsx):

    def get_opening(self, data):

        datas = {}
        data2 = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']
        query1 = '''select default_debit_account_id as account_id from account_journal where  type ='cash' and company_id = %s '''
        self.env.cr.execute(query1, (branch_ids,))
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
        res ={}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
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
		 m.date	BETWEEN %s and %s and m.company_id = %s and 
		  m.ref  is null and   (
            l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
            or
            l.user_type_id=(select id from account_account_type where name='Bank and Cash') and payment_id is not null
            or
            l.user_type_id=(select id from account_account_type where name='Bank and Cash') 
            or
            l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0
                 )
            order by  m.date                
            '''
        self.env.cr.execute(query, (date_start, date_end, branch_ids))

        for row in self.env.cr.dictfetchall():
            dates = datetime.strptime(row['dateee'], '%Y-%m-%d').date()
            res = {
                'date': dates.strftime('%d-%m-%Y'),
                'sname':row['sname'],
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
                 where  COALESCE(m.ref,'/')  !~* 'POS' and 
    		    m.date	BETWEEN %s and %s and m.company_id = %s and m.state ='posted' and
                      (
                l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
                or
                l.user_type_id=(select id from account_account_type where name='Bank and Cash') and payment_id is not null
                or
                l.user_type_id=(select id from account_account_type where name='Bank and Cash') 
                or
                l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0
                     ) 
                order by  m.date

                '''
        self.env.cr.execute(query, (date_start, date_end, branch_ids))
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
                'state': row['state'],
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


        query = '''



    select dd.dateee as dateee,dd.typess as typess,

               COALESCE(sum(CASE dd.amount WHEN dd.amount THEN dd.amount ELSE 0 END ),0)  as amount,
               COALESCE(sum(CASE dd.expense WHEN dd.expense THEN dd.expense ELSE 0 END ),0)  as expense
               from (
                select p.name as sname, m.date as dateee,m.ref as bill_no, l.name  as particular  ,l.company_id as comp_id,j.type as typess,
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

                                 (  l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance >0
                           or
                           l.user_type_id=(select id from account_account_type where name='Bank and Cash') and payment_id is not null
                           or
                           l.user_type_id=(select id from account_account_type where name='Bank and Cash')
                           or
                           l.user_type_id= (select id from account_account_type where name='Bank and Cash') and l.balance < 0 )
                            )

                           as dd group by dd.dateee,dd.typess order by dd.dateee







                              '''
        self.env.cr.execute(query, (date_start, date_end, branch_ids))


        for row in self.env.cr.dictfetchall():
            dates = datetime.strptime(row['dateee'], '%Y-%m-%d').date()
            res = {
                'date': dates.strftime('%d-%m-%Y'),
                'sname': 'POS Sale ',

                'particular': row['typess'],

                'amount': row['amount'],
                'expense': row['expense'],
            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('DAYBOOK'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 45)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 5, 20)
        company = self.env['res.company'].browse(data['form']['branch_ids']).name
        company_address = self.env['res.company'].browse(data['form']['branch_ids']).street
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()



        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})
        format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right','bold': True})
        yellow_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,
                                        'bg_color': 'fcf22f'})
        orange_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,
                                        'bg_color': 'f4a442'})
        blue_mark2 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'bold': True,
                                        'color':'000000','bg_color': 'bdb3ca','align':'center'})

        blue_mark3 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 18, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca', 'align': 'center'})

        bold = workbook.add_format({'bold': True})
        title_style = workbook.add_format({'font_size': 14,'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})
        sheet_title = [_('Date'),
                       _('Particulars'),
                       _('Debit'),
                       _('Credit')
                       ]

        sheet.merge_range('A1:D1', company, blue_mark3)
        sheet.merge_range('A2:D2', company_address, blue_mark2)
        sheet.merge_range('A3:D3', "Day Book Report", blue_mark2)
        sheet.merge_range('A4:D4',date_object_date_start.strftime('%d-%m-%Y')  + '-' + date_object_date_end.strftime('%d-%m-%Y') , blue_mark2)
        sheet.write_row(4, 0, sheet_title, title_style)

        linw_row =5
        line_column = 0

        sheet.merge_range(linw_row , 0, linw_row , 1, "Opening Balance", format1)
        sheet.write_number(linw_row , 2, self.get_opening(data), font_size_8)
        sheet.write_number(linw_row, 3, 0, font_size_8)
        linw_row = 6
        line_column = 0



        for line in self.get_lines_finalpos(data):

            if line['particular'] == 'cash':
                sheet.write(linw_row, line_column, line['date'], font_size_8)
                sheet.write(linw_row, line_column + 1,line['sname'] if line['sname'] else '/' + '' + line['particular'] if line['particular'] else '/', font_size_8)
                sheet.write(linw_row, line_column + 2, line['amount'] - line['expense'], font_size_8)
                sheet.write_number(linw_row, line_column + 3, 0, font_size_8)
            if line['particular'] == 'bank':
                sheet.write(linw_row, line_column, line['date'], font_size_8)
                sheet.write(linw_row, line_column + 1,line['sname'] if line['sname'] else '/' + '' + line['particular'] if line['particular'] else '/', font_size_8)
                sheet.write(linw_row, line_column + 2, line['amount'] - line['expense'], font_size_8)
            if line['particular'] == 'bank':
                sheet.write(linw_row, line_column, line['date'], font_size_8)
                sheet.write(linw_row, line_column + 1,line['sname'] if line['sname'] else '/' + 'To Bank' + line['particular'] if line['particular'] else '/', font_size_8)
                sheet.write(linw_row, line_column + 3, line['amount'] - line['expense'], font_size_8)
                # linw_row = linw_row + 1
            linw_row = linw_row + 1
            line_column = 0


        # for line in self.get_lines(data):
        #
        #     sheet.write(linw_row, line_column, line['date'], font_size_8)
        #     sheet.write(linw_row, line_column+1,line['sname'] if line['sname'] else '/' + ''  + line['particular'], font_size_8)
        #     sheet.write_number(linw_row, line_column+2, line['amount'], font_size_8)
        #     sheet.write_number(linw_row, line_column+3, line['expense'], font_size_8)
        #     linw_row = linw_row +1
        #     line_column=0



        for line in self.get_lines_final(data):
            sheet.write(linw_row, line_column, line['date'], font_size_8)
            sheet.write(linw_row, line_column + 1,line['sname'] if line['sname'] else '/' + '' +  line['particular'], font_size_8)

            sheet.write(linw_row, line_column + 2, line['amount'], font_size_8)
            sheet.write_number(linw_row, line_column + 3, line['expense'], font_size_8)
            linw_row = linw_row + 1
            line_column = 0

        # for line in self.get_lines_finalpos(data):
        #
        #     sheet.write(linw_row, line_column + 1, line['sname'], font_size_8)
        #     sheet.write(linw_row, line_column + 2, line['particular'], font_size_8)
        #     sheet.write_number(linw_row, line_column + 3, line['amount'], font_size_8)
        #     if line['type'] == 'bank':
        #         sheet.write(linw_row+1, line_column + 1, line['sname'] + 'To Bank', font_size_8)
        #         sheet.write(linw_row+1, line_column + 2, line['particular'], font_size_8)
        #         sheet.write_number(linw_row+1, line_column + 4, line['amount'], font_size_8)
        #         linw_row = linw_row + 1
        #     linw_row = linw_row + 1
        #     line_column = 0

        sheet.merge_range(linw_row, 0, linw_row, 1, "GRAND TOTAL", format1)

        am_cell_range = xl_range(2, 2, linw_row - 1, 2)
        ex_cell_range = xl_range(2, 3, linw_row - 1, 3)

        sheet.write_formula(linw_row, 2, '=SUM(' + am_cell_range + ')' , format1)
        sheet.write_formula(linw_row, 3, '=SUM(' + ex_cell_range + ')' , format1)

        grt_cell_range = xl_range(linw_row, 2, linw_row + 1, 2)

        # sheet.merge_range(linw_row + 2, 0, linw_row + 2, 1, "GRAND TOTAL", format1)
        #
        # sheet.write_formula(linw_row + 2, 2, '=SUM(' + grt_cell_range + ')' ,format1)

        sheet.merge_range(linw_row + 2, 0, linw_row + 2, 1, "CLOSING BALANCE", format1)

        grt_cell = xl_rowcol_to_cell(linw_row , 2)

        ex_cell = xl_rowcol_to_cell(linw_row, 3)

        sheet.write_formula(linw_row + 2, 2, '=+(' + grt_cell + '-' + ex_cell + ')',format1)

qltydaybookXls('report.qlty_daybook_xls.daybook_report_xls.xlsx', 'account.move')
