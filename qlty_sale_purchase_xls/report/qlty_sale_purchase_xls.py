from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _


class QltyCat(ReportXlsx):


    def get_lines(self, data):

        lines = []



        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        sl = 0
        query = '''select purchase_amount, sale_amount,pos_sale_amount,
                        COALESCE( ssale_date,pos_date) AS  sale_date
                    from (
                        select purchase_amount, sale_amount, COALESCE( purchase_date, sale_date) AS ssale_date from 
                            (select SUM(a.amount_total) as purchase_amount,a.date_invoice as purchase_date from account_invoice as a
                                where a.type='in_invoice' and a.state in ('open','paid') and
                                a.company_id = %s and a.date_invoice BETWEEN %s and %s
                                GROUP BY a.date_invoice) aa
                        full join 

                        (select SUM(a.amount_total) as sale_amount,a.date_invoice as sale_date from account_invoice as a
                            where a.type='out_invoice' and a.state in ('open','paid') and
                            a.company_id = %s and a.date_invoice BETWEEN %s and %s
                            GROUP BY a.date_invoice) bb
                            on aa.purchase_date =bb.sale_date) aaa
                    full join
                
                        (select SUM(round(((pol.qty * pol.price_unit) - pol.discount),2) ) as pos_sale_amount,CAST(po.date_order AS DATE) as pos_date from pos_order_line as pol
                            left join pos_order as po
                            on po.id=pol.order_id
                            where  po.state in ('done','paid') and
                            po.company_id = %s and CAST(po.date_order AS DATE) BETWEEN %s and %s
                            GROUP BY CAST(po.date_order AS DATE)) cc
                            on aaa.ssale_date =cc.pos_date
                            order by sale_date




                        '''
        self.env.cr.execute(query,(company_id, date_start, date_end,
                                   company_id, date_start, date_end,
                                   company_id, date_start, date_end))
        for row in self.env.cr.dictfetchall():
            sl +=1
            sale_amount = row['sale_amount'] if row['sale_amount'] else 0
            pos_amount = row['pos_sale_amount'] if row['pos_sale_amount'] else 0

            dates = datetime.strptime(row['sale_date'], '%Y-%m-%d').date()

            res = {
                'sl_no': sl,
                'date': dates.strftime('%d-%m-%Y'),
                'sale': sale_amount+pos_amount,
                'purchase': row['purchase_amount']if row['purchase_amount'] else 0

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

        date_end = data['form']['date_end']
        # category_id = data['form']['category_id']
        #
        # for i in category_id:
        #
        #     category_name = self.env["pdct.category"].browse(i).name

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

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()

        sheet.merge_range('B1:D1', company, format2)
        sheet.merge_range('B2:D2', company_address, format2)
        sheet.merge_range('B3:D3', "Date Wise Sale & Purchase Analysis ", format2)
        sheet.merge_range('B4:D4', date_object_date_start.strftime('%d-%m-%Y') + ' - ' + date_object_date_end.strftime('%d-%m-%Y'), format2)

        # sheet.merge_range('A1:B1', "Category Wise Report ", format1)
        # sheet.write('C1', category_name, format1)
        # sheet.write('D1', "DATE :-", format1)
        # sheet.merge_range('E1:F1', date_start + ' - ' + date_end, format1)

        sheet.write('A6', "Sl No", blue_mark)
        sheet.write('B6', "Date", blue_mark)
        sheet.write('C6', "Sale", blue_mark)
        sheet.write('D6', "Purchase", blue_mark)

        linw_row = 6

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['date'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['sale'], font_size_8)
            sheet.write(linw_row, line_column + 3, line['purchase'], font_size_8)
            # sheet.write(linw_row, line_column + 4, line['s_qty'], font_size_8)
            # sheet.write(linw_row, line_column + 5, line['sale'], font_size_8)
            # sheet.write(linw_row, line_column + 6, line['profit'], font_size_8)
            # sheet.write(linw_row, line_column + 7, line['onhand'], font_size_8)
            # sheet.write_number(linw_row, line_column + 8, line['profit'], font_size_8)
            # sheet.write_number(linw_row, line_column + 9, line['without_tax'], font_size_8)

            # for line2 in self.get_lines_two(data):
            #
            #     if line2['t_name'] == 'Tax 5%' and line2['inv_id'] == line['inv_id']:
            #         sheet.write_number(linw_row, line_column + 10, line2['t_amount'], font_size_8)
            #         sheet.write_number(linw_row, line_column + 11, (line2['t_amount']) / 2, font_size_8)
            #         sheet.write_number(linw_row, line_column + 12, (line2['t_amount']) / 2, font_size_8)
            #
            #     if line2['t_name'] == 'Tax 12%' and line2['inv_id'] == line['inv_id']:
            #         sheet.write_number(linw_row, line_column + 13, line2['t_amount'], font_size_8)
            #         sheet.write_number(linw_row, line_column + 14, (line2['t_amount']) / 2, font_size_8)
            #         sheet.write_number(linw_row, line_column + 15, (line2['t_amount']) / 2, font_size_8)
            #
            #     if line2['t_name'] == 'Tax 18%' and line2['inv_id'] == line['inv_id']:
            #         sheet.write_number(linw_row, line_column + 16, line2['t_amount'], font_size_8)
            #         sheet.write_number(linw_row, line_column + 17, (line2['t_amount']) / 2, font_size_8)
            #         sheet.write_number(linw_row, line_column + 18, (line2['t_amount']) / 2, font_size_8)
            #
            #     if line2['t_name'] == 'Tax 28%' and line2['inv_id'] == line['inv_id']:
            #         sheet.write_number(linw_row, line_column + 19, line2['t_amount'], font_size_8)
            #         sheet.write_number(linw_row, line_column + 20, (line2['t_amount']) / 2, font_size_8)
            #         sheet.write_number(linw_row, line_column + 21, (line2['t_amount']) / 2, font_size_8)
            #
            #     if line2['t_name'] == 'Tax 0%' and line2['inv_id'] == line['inv_id']:
            #         sheet.write_number(linw_row, line_column + 22, line2['t_amount'], font_size_8)
            #
            #     if line2['t_name'] == 'IGST' and line2['inv_id'] == line['inv_id']:
            #         sheet.write_number(linw_row, line_column + 23, line2['t_amount'], font_size_8)

            linw_row = linw_row + 1
            line_column = 0

        line_column = 0

        # if line['t_name'] == 'Tax 5%':
        #     sheet.write_number(linw_row, line_column + 9, line['t_amount'], font_size_8)
        #
        # if line['t_name'] == 'Tax 18%':
        #     sheet.write_number(linw_row, line_column + 9, line['t_amount'], font_size_8)

        # linw_row = linw_row + 1
        # line_column = 0



        #   #      sheet.merge_range(linw_row,0,linw_row,2, "TOTAL", format1)

        sheet.merge_range(linw_row, 0,linw_row, 1, "TOTAL", format1)

        total_cell_range11 = xl_range(3, 2, linw_row - 1, 2)
        total_cell_range = xl_range(3, 3, linw_row - 1, 3)
        # total_cell_range_one = xl_range(3, 6, linw_row - 1, 6)
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


        sheet.write_formula(linw_row, 2, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 3, '=SUM(' + total_cell_range + ')', format1)
        # sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_one + ')', format1)
        # sheet.write_formula(linw_row, 10, '=SUM(' + total_cell_range_three + ')', format1)
        # sheet.write_formula(linw_row, 11, '=SUM(' + total_cell_range_four + ')', format1)
        # sheet.write_formula(linw_row, 12, '=SUM(' + total_cell_range11 + ')', format1)
        # sheet.write_formula(linw_row, 13, '=SUM(' + total_cell_range13 + ')', format1)
        # sheet.write_formula(linw_row, 14, '=SUM(' + total_cell_range14 + ')', format1)
        # sheet.write_formula(linw_row, 15, '=SUM(' + total_cell_range15 + ')', format1)
        # sheet.write_formula(linw_row, 16, '=SUM(' + total_cell_range16 + ')', format1)
        # sheet.write_formula(linw_row, 17, '=SUM(' + total_cell_range17 + ')', format1)
        # sheet.write_formula(linw_row, 18, '=SUM(' + total_cell_range18 + ')', format1)
        # sheet.write_formula(linw_row, 19, '=SUM(' + total_cell_range19 + ')', format1)
        # sheet.write_formula(linw_row, 20, '=SUM(' + total_cell_range20 + ')', format1)
        # sheet.write_formula(linw_row, 21, '=SUM(' + total_cell_range21 + ')', format1)
        # sheet.write_formula(linw_row, 22, '=SUM(' + total_cell_range22 + ')', format1)
        # sheet.write_formula(linw_row, 23, '=SUM(' + total_cell_range23 + ')', format1)


QltyCat('report.qlty_sale_purchase_xls.qlty_sale_purchase_xls.xlsx', 'sale.order')
