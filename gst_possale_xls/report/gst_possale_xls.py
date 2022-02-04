from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _


class possaleXls(ReportXlsx):



    def get_lines(self, data):
        lines = []
        res ={}

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']

        query = '''
        SELECT  ROW_NUMBER() OVER(ORDER BY dd.odate ASC) AS slno,
        dd.posid as id,dd.odate as pdate,dd.oname as pname,
COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.total ELSE 0 END ),0)  as totalamount,
COALESCE(sum(CASE dd.posid WHEN dd.posid THEN dd.untaxamount ELSE 0 END ),0)  as untaxamount,
COALESCE(sum(CASE dd.tamount  WHEN 0 THEN dd.taxamount ELSE 0 END ),0)  as tax0,
COALESCE(sum(CASE dd.tamount WHEN 5 THEN dd.taxamount ELSE 0 END ),0)  as tax5,
COALESCE(sum(CASE dd.tamount WHEN 12 THEN dd.taxamount ELSE 0 END ),0)  as tax12,
COALESCE(sum(CASE dd.tamount WHEN 18 THEN dd.taxamount ELSE 0 END ),0)  as tax18,
COALESCE(sum(CASE dd.tamount WHEN 28 THEN dd.taxamount ELSE 0 END ),0)  as tax28

 from
(

SELECT 
  pos_order.id as posid, 
  pos_order.date_order as odate,
  
  account_tax.name as tname,
  account_tax.amount as tamount,  
  pos_order.name as oname, 
  round(((pos_order_line.qty * pos_order_line.price_unit) - pos_order_line.discount),2) as total,
  round(((pos_order_line.qty * pos_order_line.price_unit) - pos_order_line.discount) * (account_tax.amount/(100+account_tax.amount)),2) as taxamount, 
  round(((pos_order_line.qty * pos_order_line.price_unit) - pos_order_line.discount) * 100 / (100+account_tax.amount),2)  as untaxamount
FROM 
  public.pos_order, 
  public.pos_order_line, 
  public.account_tax_pos_order_line_rel, 
  public.account_tax
WHERE 
  pos_order.id = pos_order_line.order_id AND
  pos_order_line.id = account_tax_pos_order_line_rel.pos_order_line_id AND 
  account_tax_pos_order_line_rel.account_tax_id = account_tax.id 
  AND pos_order.state in ('paid','done')  
  AND to_char(date_trunc('day',pos_order.date_order),'YYYY-MM-DD')::date between %s and %s  
  AND pos_order_line.company_id='1' 

   group by account_tax.name ,pos_order.id,pos_order_line.qty,pos_order_line.discount,
  account_tax.amount,pos_order_line.price_unit  
  
   ) as dd  group by dd.posid,dd.oname,dd.odate order by dd.odate
                '''

        # self.env.cr.execute(query,(date_start,date_end))

        # self.env.cr.execute(query,(tuple(date_start),tuple(date_end)))
        self.env.cr.execute(query, (date_start, date_end))

        for row in self.env.cr.dictfetchall():
            res = {
                'sl_no': row['slno'],
                'inv_date': row['pdate'],
                'inv_no': row['pname'],
                'total': row['totalamount'],
                'without_tax': row['untaxamount'] ,
                'c_type': 'POS Sale',
                'tax0': row['tax0'],
                'tax5': row['tax5'],
                'tax12': row['tax12'],
                'tax18': row['tax18'],
                'tax28': row['tax28']

            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('purchase'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)

        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 20)
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

        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True})

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

        sheet.merge_range('A1:B1', "GST POS SALE Report ", format1)
        sheet.write('D1', "DATE :-", format1)
        sheet.merge_range('E1:F1', date_start + ' - ' + date_end, format1)

        sheet.write('A3', "Sl No", blue_mark)
        sheet.write('B3', "Date", blue_mark)
        # sheet.write('C3', "Particulars", blue_mark)
        # sheet.write('D3', "Supplier", blue_mark)
        # sheet.write('E3', "Address ", blue_mark)
        sheet.write('C3', "Voucher Type ", blue_mark)
        sheet.write('D3', "Voc No", blue_mark)
        # sheet.write('H3', "GSTIN/UIN", blue_mark)
        sheet.write('E3', "POS SALE Total", blue_mark)
        sheet.write('F3', "With Out Tax", blue_mark)
        sheet.write('G3', "SALE-0%", blue_mark)
        sheet.write('H3', "SALE-5%", blue_mark)
        # sheet.write('L3', "S GST-2.5%", blue_mark)
        # sheet.write('M3', "C GST-2.5%", blue_mark)
        sheet.write('I3', "SALE-12%", blue_mark)
        # sheet.write('O3', "S GST-6%", blue_mark)
        # sheet.write('P3', "C GST-6%", blue_mark)
        sheet.write('J3', "SALE-18%", blue_mark)
        # sheet.write('R3', "S GST-9%", blue_mark)
        # sheet.write('S3', "C GST-9%", blue_mark)
        sheet.write('K3', "SALE-28%", blue_mark)
        # sheet.write('U3', "S GST-14%", blue_mark)
        # sheet.write('V3', "C GST-14%", blue_mark)
        sheet.write('L3', "", blue_mark)
        # sheet.write('P3', "IGST", blue_mark)
        linw_row = 3

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['inv_date'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['c_type'], font_size_8)
            sheet.write(linw_row, line_column + 3, line['inv_no'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['total'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['without_tax'], font_size_8)
            sheet.write(linw_row, line_column + 6, line['tax0'], font_size_8)
            sheet.write(linw_row, line_column + 7, line['tax5'], font_size_8)
            sheet.write_number(linw_row, line_column + 8, line['tax12'], font_size_8)
            sheet.write_number(linw_row, line_column + 9, line['tax18'], font_size_8)
            sheet.write_number(linw_row, line_column + 10, line['tax28'], font_size_8)
            # sheet.write_number(linw_row, line_column + 11, line['tax5'], font_size_8)
            # sheet.write_number(linw_row, line_column + 12, line['tax12'], font_size_8)
            # sheet.write_number(linw_row, line_column + 13, line['tax18'], font_size_8)
            # sheet.write_number(linw_row, line_column + 14, line['tax28'], font_size_8)

            # for line2 in self.get_lines_two(data):
            #
            #     if line2['t_name'] == 'Tax 5%' and line2['inv_id'] == line['inv_id']:
            #         sheet.write_number(linw_row, line_column + 10, line2['t5_amount'], font_size_8)
            #         sheet.write_number(linw_row, line_column + 11, (line2['t_amount']) / 2, font_size_8)
            #         sheet.write_number(linw_row, line_column + 12, (line2['t_amount']) / 2, font_size_8)
            #
            #     if line2['t_name'] == 'Tax 12%' and line2['inv_id'] == line['inv_id']:
            #         sheet.write_number(linw_row, line_column + 13, line2['t12_amount'], font_size_8)
            #         sheet.write_number(linw_row, line_column + 14, (line2['t_amount']) / 2, font_size_8)
            #         sheet.write_number(linw_row, line_column + 15, (line2['t_amount']) / 2, font_size_8)
            #
            #     if line2['t_name'] == 'Tax 18%' and line2['inv_id'] == line['inv_id']:
            #         sheet.write_number(linw_row, line_column + 16, line2['t18_amount'], font_size_8)
            #         sheet.write_number(linw_row, line_column + 17, (line2['t_amount']) / 2, font_size_8)
            #         sheet.write_number(linw_row, line_column + 18, (line2['t_amount']) / 2, font_size_8)
            #
            #     if line2['t_name'] == 'Tax 28%' and line2['inv_id'] == line['inv_id']:
            #         sheet.write_number(linw_row, line_column + 19, line2['t28_amount'], font_size_8)
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

        sheet.write(linw_row, 0, "TOTAL", format1)

        total_cell_range11 = xl_range(3, 4, linw_row - 1, 4)
        total_cell_range = xl_range(3, 5, linw_row - 1, 5)
        total_cell_range_one = xl_range(3, 6, linw_row - 1, 6)
        total_cell_range_two = xl_range(3, 7, linw_row - 1, 7)
        total_cell_range_three = xl_range(3, 8, linw_row - 1, 8)
        total_cell_range_four = xl_range(3, 9, linw_row - 1, 9)
        total_cell_range12 = xl_range(3, 10, linw_row - 1, 10)

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


        sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 5, '=SUM(' + total_cell_range + ')', format1)
        sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_one + ')', format1)
        sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range_two + ')', format1)
        sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range_three + ')', format1)
        sheet.write_formula(linw_row, 9, '=SUM(' + total_cell_range_four + ')', format1)
        sheet.write_formula(linw_row, 10, '=SUM(' + total_cell_range12 + ')', format1)
        # sheet.write_formula(linw_row, 11, '=SUM(' + total_cell_range13 + ')', format1)
        # sheet.write_formula(linw_row, 12, '=SUM(' + total_cell_range14 + ')', format1)
        # sheet.write_formula(linw_row, 15, '=SUM(' + total_cell_range15 + ')', format1)
        # sheet.write_formula(linw_row, 16, '=SUM(' + total_cell_range16 + ')', format1)
        # sheet.write_formula(linw_row, 17, '=SUM(' + total_cell_range17 + ')', format1)
        # sheet.write_formula(linw_row, 18, '=SUM(' + total_cell_range18 + ')', format1)
        # sheet.write_formula(linw_row, 19, '=SUM(' + total_cell_range19 + ')', format1)
        # sheet.write_formula(linw_row, 20, '=SUM(' + total_cell_range20 + ')', format1)
        # sheet.write_formula(linw_row, 21, '=SUM(' + total_cell_range21 + ')', format1)
        # sheet.write_formula(linw_row, 22, '=SUM(' + total_cell_range22 + ')', format1)
        # sheet.write_formula(linw_row, 23, '=SUM(' + total_cell_range23 + ')', format1)


possaleXls('report.gst_possale_xls.possale_report_xls.xlsx', 'account.move')
