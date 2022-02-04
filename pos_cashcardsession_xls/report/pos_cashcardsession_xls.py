from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _


class pos_cashcardsession_xls(ReportXlsx):


    def get_lines(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']
        pos_config_id = data['form']['pos_config_ids']

        if not counter_only:

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
                            
                            GROUP BY CAST(pos.start_at AS DATE),abs.amount,po.name,aj.type ,pos.name
                            ) as dd 
                            GROUP BY dd.start_at,dd.pname order by dd.start_at,dd.pname
                        
                        '''

            self.env.cr.execute(query, (company_id, date_start, date_end))
            for row in self.env.cr.dictfetchall():
                sl += 1
                dates = datetime.strptime(row['pos_date'], '%Y-%m-%d').date()

                res = {
                    'sl_no': sl,
                    'pname': row['pname'],
                    'date': dates.strftime('%d-%m-%Y'),
                    'total': row['total'] if row['total'] else 0,
                    'cash': row['cashtotal'] if row['cashtotal'] else 0,
                    'card': row['cardtotal'] if row['cardtotal'] else 0

                }
                lines.append(res)
        else:

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
                            and pos.config_id= %s
                            GROUP BY CAST(pos.start_at AS DATE),abs.amount,po.name,aj.type ,pos.name
                            ) as dd 
                            GROUP BY dd.start_at,dd.pname order by dd.start_at,dd.pname


                                   '''

            self.env.cr.execute(query, (company_id, date_start, date_end,pos_config_id))
            for row in self.env.cr.dictfetchall():
                sl += 1
                dates = datetime.strptime(row['pos_date'], '%Y-%m-%d').date()

                res = {
                    'sl_no': sl,
                    'pname': row['pname'],
                    'date': dates.strftime('%d-%m-%Y'),
                    'total': row['total'] if row['total'] else 0,
                    'cash': row['cashtotal'] if row['cashtotal'] else 0,
                    'card': row['cardtotal'] if row['cardtotal'] else 0

                }
                lines.append(res)


        if lines:
            return lines
        else:
            return []


    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Date Wise Sale - Purchase'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 8)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 18)
        sheet.set_column(4, 4, 18)
        sheet.set_column(5, 5, 18)
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


        company = self.env["res.company"].browse(data['form']['company_id']).name

        company_address= self.env["res.company"].browse(data['form']['company_id']).street


        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True})

        format2 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True,'align':'center'})

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
        blue_mark2 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'bold': True,
                                        'color':'000000','bg_color': 'bdb3ca','align':'center'})



        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()

        sheet.merge_range('B1:E1', company, blue_mark2)
        sheet.merge_range('B2:E2', company_address, blue_mark2)
        sheet.merge_range('B3:E3', "POS Sale Card And Cash", blue_mark2)
        sheet.merge_range('B4:E4', date_object_date_start.strftime('%d-%m-%Y') + ' - ' + date_object_date_end.strftime('%d-%m-%Y'), blue_mark2)



        sheet.write('A6', "Sl No", blue_mark)
        sheet.write('B6', "DATE", blue_mark)
        sheet.write('C6', "SESSION", blue_mark)
        sheet.write('D6', "TOTAL", blue_mark)
        sheet.write('E6', "CASH", blue_mark)
        sheet.write('F6', "CARD", blue_mark)

        linw_row = 6

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['date'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['pname'], font_size_8)
            sheet.write(linw_row, line_column + 3, line['total'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['cash'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['card'], font_size_8)

            linw_row = linw_row + 1
            line_column = 0

        sheet.merge_range(linw_row, 0,linw_row, 2, "TOTAL", format1)

        total_cell_range11 = xl_range(3, 3, linw_row - 1, 3)
        total_cell_range = xl_range(3, 4, linw_row - 1, 4)
        total_cell_range12 = xl_range(3, 5, linw_row - 1, 5)
        sheet.write_formula(linw_row, 3, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range + ')', format1)
        sheet.write_formula(linw_row, 5, '=SUM(' + total_cell_range12 + ')', format1)


pos_cashcardsession_xls('report.pos_cashcardsession_xls.pos_cashcardsession_xls.xlsx', 'sale.order')
