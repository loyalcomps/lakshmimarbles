from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime

class Gst_purchase_Reg_Xls(ReportXlsx):

    def get_opening(self, data):
        datas = {}
        data2 = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        value = 0
        return value


    def get_lines(self, data):

        lines = []
        res = {}
        val = {}
        inv = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']

        query = '''
       Select
 ROW_NUMBER() OVER(ORDER BY dd.date_invoice ASC) AS sl_no,
dd.date_invoice as date_invoice,
dd.sreference as move_name,
dd.amount_total as amount_total,
dd.amount_untaxed as amount_untaxed,
dd.amount_tax as amount_tax,
dd.amount_discount as amount_discount,

dd.ppname as ppname,
dd.ppaddress as ppaddress,
dd.gstin as gstin,

COALESCE(sum(CASE dd.t_amount  WHEN 0 THEN dd.tax_amount ELSE 0 END ),0)  as tax0,
COALESCE(sum(CASE dd.t_amount WHEN 5 THEN dd.tax_amount ELSE 0 END ),0)  as tax5,
COALESCE(sum(CASE dd.t_amount WHEN 12 THEN dd.tax_amount ELSE 0 END ),0)  as tax12,
COALESCE(sum(CASE dd.t_amount WHEN 18 THEN dd.tax_amount ELSE 0 END ),0)  as tax18,
COALESCE(sum(CASE dd.t_amount WHEN 28 THEN dd.tax_amount ELSE 0 END ),0)  as tax28

from (


  SELECT avt.invoice_id as invoice_id,j.date_invoice as date_invoice,
    j.reference as sreference,
    round(j.amount_total,2) as amount_total,
    round(j.amount_untaxed,2) as amount_untaxed,
    round(j.amount_tax,2) as amount_tax,
    round(j.amount_discount,2) as amount_discount,
    p.name as ppname,
    p.street as ppaddress,
    avt.name,
    tax.amount as t_amount,
    round(avt.amount,2) tax_amount,
    p.gst_in as gstin
    from account_invoice as j left join 
    account_invoice_tax as avt on ( j.id=avt.invoice_id) left join 
    res_partner as p on (p.id=j.partner_id)
    left join account_tax as tax on (tax.id=avt.tax_id)
    where 
    j.date_invoice BETWEEN %s and %s   and j.company_id = %s  and 
    j.state in ('open','paid')  and j.type='in_invoice'    
    order by j.date_invoice


    
    ) as dd group by dd.date_invoice,dd.sreference,dd.amount_total,dd.amount_untaxed,dd.ppname,dd.ppaddress,dd.gstin,dd.amount_tax,dd.amount_discount
           
           '''

        self.env.cr.execute(query, (date_start, date_end, company_id ))

        # lines = self.env.cr.dictfetchall()

        for row in self.env.cr.dictfetchall():
            dates = datetime.strptime(row['date_invoice'], '%Y-%m-%d').date()

            res = {
                'sl_no': row['sl_no'],
                'date_invoice': dates.strftime('%d-%m-%Y'),
                'ppname': row['ppname'],
                'ppaddress': row['ppaddress'],
                'gstin': row['gstin'],
                'move_name': row['move_name'],
                'amount_total': row['amount_total'],
                'amount_untaxed': row['amount_untaxed'],
                'amount_taxed' : row['amount_tax'],
                'amount_discount': row['amount_discount'],
                'tax0': row['tax0'],
                'tax5': row['tax5'],
                'tax12': row['tax12'],
                'tax18': row['tax18'],
                'tax28': row['tax28'],
                'c_type': 'Purchase'

            }
            lines.append(res)

        if lines:

            return lines
        else:
            return []



    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('B2B'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)

        sheet.set_column(0, 0, 7)
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

        sheet.merge_range('A1:B1', "GST Purchase Report ", format1)
        sheet.write('D1', "DATE :-", format1)
        sheet.merge_range('E1:F1', date_start + ' - ' + date_end, format1)

        sheet.write('A3', "Sl No", blue_mark)
        sheet.write('B3', "Date", blue_mark)
        sheet.write('C3', "Particulars", blue_mark)
        sheet.write('D3', "Supplier", blue_mark)
        sheet.write('E3', "Address ", blue_mark)
        sheet.write('F3', "Voucher Type ", blue_mark)
        sheet.write('G3', "Voc No", blue_mark)
        sheet.write('H3', "GSTIN/UIN", blue_mark)
        sheet.write('I3', "Purchase Total", blue_mark)
        sheet.write('J3', "Untaxable Value", blue_mark)
        sheet.write('K3', "Taxable Value", blue_mark)
        sheet.write('L3', "Discount Value", blue_mark)
        sheet.write('M3', "Purchase-NonTaxble", blue_mark)
        # sheet.write('L3', "S GST-2.5%", blue_mark)
        # sheet.write('M3', "C GST-2.5%", blue_mark)
        sheet.write('N3', "Purchase-5%", blue_mark)
        # sheet.write('O3', "S GST-6%", blue_mark)
        # sheet.write('P3', "C GST-6%", blue_mark)
        sheet.write('O3', "Purchase-12%", blue_mark)
        # sheet.write('R3', "S GST-9%", blue_mark)
        # sheet.write('S3', "C GST-9%", blue_mark)
        sheet.write('P3', "Purchase-18%", blue_mark)
        # sheet.write('U3', "S GST-14%", blue_mark)
        # sheet.write('V3', "C GST-14%", blue_mark)
        sheet.write('Q3', "Purchase-28%", blue_mark)
        sheet.write('R3', "IGST", blue_mark)
        linw_row = 3

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['date_invoice'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['ppname'], font_size_8)
            sheet.write(linw_row, line_column + 3, line['ppname'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['ppaddress'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['c_type'], font_size_8)
            sheet.write(linw_row, line_column + 6, line['move_name'], font_size_8)
            sheet.write(linw_row, line_column + 7, line['gstin'], font_size_8)
            sheet.write_number(linw_row, line_column + 8, line['amount_total'], font_size_8)
            sheet.write_number(linw_row, line_column + 9, line['amount_untaxed'], font_size_8)
            sheet.write_number(linw_row, line_column + 10, line['amount_taxed'], font_size_8)
            sheet.write_number(linw_row, line_column + 11, line['amount_discount'], font_size_8)
            sheet.write_number(linw_row, line_column + 12, line['tax0'], font_size_8)
            sheet.write_number(linw_row, line_column + 13, line['tax5'], font_size_8)
            sheet.write_number(linw_row, line_column + 14, line['tax12'], font_size_8)
            sheet.write_number(linw_row, line_column + 15, line['tax18'], font_size_8)
            sheet.write_number(linw_row, line_column + 16, line['tax28'], font_size_8)

            linw_row = linw_row + 1
            line_column = 0

        line_column = 0


        sheet.write(linw_row, 0, "TOTAL", format1)


        # total_cell_range = xl_range(3, 7, linw_row - 1, 7)
        total_cell_range_one = xl_range(3, 8, linw_row - 1, 8)
        total_cell_range_two = xl_range(3, 9, linw_row - 1, 9)
        total_cell_range_three = xl_range(3, 10, linw_row - 1, 10)
        total_cell_range_four = xl_range(3, 11, linw_row - 1, 11)
        total_cell_range11 = xl_range(3, 12, linw_row - 1, 12)
        total_cell_range13 = xl_range(3, 13, linw_row - 1, 13)
        total_cell_range14 = xl_range(3, 14, linw_row - 1, 14)
        total_cell_range15 = xl_range(3, 15, linw_row - 1, 15)
        total_cell_range16 = xl_range(3, 16, linw_row - 1, 16)
        total_cell_range17 = xl_range(3, 17, linw_row - 1, 17)
        # total_cell_range18 = xl_range(3, 18, linw_row - 1, 18)
        # total_cell_range19 = xl_range(3, 19, linw_row - 1, 19)
        # total_cell_range20 = xl_range(3, 20, linw_row - 1, 20)
        # total_cell_range21 = xl_range(3, 21, linw_row - 1, 21)
        # total_cell_range22 = xl_range(3, 22, linw_row - 1, 22)
        # total_cell_range23 = xl_range(3, 23, linw_row - 1, 23)

        # sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range + ')', format1)
        sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range_one + ')', format1)
        sheet.write_formula(linw_row, 9, '=SUM(' + total_cell_range_two + ')', format1)
        sheet.write_formula(linw_row, 10, '=SUM(' + total_cell_range_three + ')', format1)
        sheet.write_formula(linw_row, 11, '=SUM(' + total_cell_range_four + ')', format1)
        sheet.write_formula(linw_row, 12, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 13, '=SUM(' + total_cell_range13 + ')', format1)
        sheet.write_formula(linw_row, 14, '=SUM(' + total_cell_range14 + ')', format1)
        sheet.write_formula(linw_row, 15, '=SUM(' + total_cell_range15 + ')', format1)
        sheet.write_formula(linw_row, 16, '=SUM(' + total_cell_range16 + ')', format1)
        sheet.write_formula(linw_row, 17, '=SUM(' + total_cell_range17 + ')', format1)
        # sheet.write_formula(linw_row, 18, '=SUM(' + total_cell_range18 + ')', format1)
        # sheet.write_formula(linw_row, 19, '=SUM(' + total_cell_range19 + ')', format1)
        # sheet.write_formula(linw_row, 20, '=SUM(' + total_cell_range20 + ')', format1)
        # sheet.write_formula(linw_row, 21, '=SUM(' + total_cell_range21 + ')', format1)
        # sheet.write_formula(linw_row, 22, '=SUM(' + total_cell_range22 + ')', format1)
        # sheet.write_formula(linw_row, 23, '=SUM(' + total_cell_range23 + ')', format1)


Gst_purchase_Reg_Xls('report.gsttwo_purchase_reg_xls.income_purchase_xls.xlsx', 'account.invoice')
