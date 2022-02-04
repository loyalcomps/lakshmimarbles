from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _


class Vendorbill(ReportXlsx):


    def get_lines(self, data):

        lines = []



        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        vendor_id=data['form']['vendor_id']
        sl = 0
        query = ''' 
        
     
                    select COALESCE(dd.p_date) AS  pdate,
                               dd.amount as amount,dd.number as number,dd.reference as reference,dd.breference as breference,dd.pname as pname,dd.jname as ajname
                                from (
                                select abs.amount as amount,abs.check_number as number,abs.cheque_reference as reference,abs.bank_reference as breference,
                                COALESCE(abs.payment_date) AS  p_date,
                                abs.payment_type ptype,po.name as pname,aj.name as jname,
                                CAST(abs.payment_date AS DATE) as start_at from
                                       account_payment as abs
                                        left join account_payment_method as po on po.id=abs.payment_method_id
                                        left join account_journal as aj  on aj.id=abs.journal_id
                                        where  po.payment_type in ('outbound','inbound') and 
            				abs.company_id = %s and abs.partner_id=%s
            				and CAST(abs.payment_date AS DATE) between %s and %s

                                        GROUP BY CAST(abs.payment_date AS DATE),abs.amount,abs.check_number,abs.cheque_reference,
                                        po.name,aj.name,
                                        abs.bank_reference,abs.payment_type
                                        ) as dd order by dd.p_date
        '''

        self.env.cr.execute(query, (
                                company_id, vendor_id,date_start, date_end,
                                    ))
        for row in self.env.cr.dictfetchall():

            sl += 1


            # date = datetime.strptime(row['pdate'], '%Y-%m-%d').date()

            res = {
                'date':row['pdate'] if row['pdate'] else " ",
                'sl_no': sl,
                'amount':row['amount'] if row['amount'] else " ",
                'reference':row['reference'] if row['reference'] else " ",
                'breference': row['breference'] if row['breference'] else " ",
                'pname': row['pname'] if row['pname'] else " ",
                'ajname': row['ajname'] if row['ajname'] else " ",
                'number': row['number'] if row['number'] else " ",

            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Payment Report'))
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
        sheet.set_default_row(20)

        # sheet.fit_to_pages(1, 0)
        # sheet.set_zoom(80)
        # sheet.set_column(0, 0, 8)
        # sheet.set_column(1, 1, 20)
        # sheet.set_column(2, 2, 25)
        # sheet.set_column(3, 3, 25)
        # sheet.set_column(4, 4, 20)
        # sheet.set_column(5, 5, 10)
        # sheet.set_column(6, 6, 20)
        # sheet.set_column(7, 7, 20)
        # sheet.set_column(8, 8, 20)
        # sheet.set_column(9, 9, 20)
        # sheet.set_column(10, 10, 20)
        # sheet.set_column(11, 11, 20)
        # sheet.set_column(12, 12, 20)
        # sheet.set_column(13, 13, 20)
        # sheet.set_column(14, 14, 20)
        # sheet.set_column(15, 15, 20)
        # sheet.set_column(16, 16, 20)
        # sheet.set_column(17, 17, 20)
        # sheet.set_column(18, 18, 20)
        # sheet.set_column(19, 19, 20)
        # sheet.set_column(20, 20, 20)

        date_start = data['form']['date_start']

        date_end = data['form']['date_end']


        company = self.env["res.company"].browse(data['form']['company_id']).name

        company_address= self.env["res.company"].browse(data['form']['company_id']).street


        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        font_size_88 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'align': 'center'})


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
             'color': 'ffffff', 'bg_color': '483D8B',})
        blue_mark1 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': 'ffffff', 'bg_color': '483D8B', 'align': 'center'})

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()

        sheet.merge_range('A1:H1', company, format2)
        sheet.merge_range('A2:H2', company_address, format2)
        sheet.merge_range('A3:H3', "Payment Report", format2)
        sheet.merge_range('A4:H4', date_object_date_start.strftime('%d-%m-%Y') + ' - ' + date_object_date_end.strftime('%d-%m-%Y'), format2)
        sheet.merge_range('A5:H5', " ", format2)



        # sheet.merge_range('A1:B1', "Category Wise Report ", format1)
        # sheet.write('C1', category_name, format1)
        # sheet.write('D1', "DATE :-", format1)
        # sheet.merge_range('E1:F1', date_start + ' - ' + date_end, format1)

        sheet.write('A8', "Sl No", blue_mark1)
        sheet.write('B8', "Date", blue_mark1)
        sheet.write('C8', "Payment Method", blue_mark1)
        sheet.write('D8', "Payment Journal", blue_mark1)
        sheet.write('E8', "CHECK number", blue_mark1)
        sheet.write('F8', "BANK Reference", blue_mark1)
        sheet.write('G8', "CHECK Reference", blue_mark1)
        sheet.write('H8', "Amount", blue_mark1)






        linw_row = 8

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_88)
            sheet.write(linw_row, line_column + 1, line['date'], font_size_88)
            sheet.write(linw_row, line_column + 2, line['pname'], font_size_8)
            sheet.write(linw_row, line_column + 3, line['ajname'], font_size_8)
            sheet.write(linw_row, line_column + 4, (line['number']), font_size_8)
            sheet.write(linw_row, line_column + 5, (line['breference']), font_size_8)
            sheet.write(linw_row, line_column + 6, (line['reference']), font_size_8)
            sheet.write(linw_row, line_column + 7, (line['amount']), font_size_8)







            linw_row = linw_row + 1
            line_column = 0

        line_column = 0


        sheet.merge_range(linw_row, 0,linw_row, 1, "TOTAL", format1)

        total_cell_range11 = xl_range(8, 2, linw_row - 1, 2)
        total_cell_range = xl_range(8, 7, linw_row - 1, 3)

        # sheet.write_formula(linw_row, 2, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range + ')', format1)

Vendorbill('report.bill_payment_xls.bill_payment_xls.xlsx', 'account.move')
