from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _


class Gst_posale_Reg_Xls(ReportXlsx):


    def get_opening(self, data):
 
        datas = {}
        data2 = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        value = 0
        return value

    def get_lines_two(self, data):

        lines = []
        res = {}
        val = {}
        inv = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        company_id = data['form']['company_id']

        inv_ids = self.env["pos.order"].search([('date_order', '>=', date_start),
                                                      ('date_order', '<=', date_end),
                                                      ('company_id', '=', company_id),
                                                      ('state', 'in', ['paid', 'posted','done'])]).sorted('date_order')


        tax_ids = self.env["account.tax"].search([])
        tot = 0



        for j in inv_ids:
            pos_lines =  self.env["pos.order.line"].search([('order_id', '=',j.id )])

            tot = 0
            t5t_tax = 0
            t12t_tax = 0
            t18t_tax = 0
            t28t_tax = 0
            t5_tax = 0
            t12_tax = 0
            t18_tax = 0
            t28_tax = 0
            t0_zerotax = 0
            kname = "Tax 0%"

            for i in pos_lines:
                if i.tax_ids_after_fiscal_position:

                    for k in i.tax_ids_after_fiscal_position:

                    # for k in i.invoice_line_tax_ids:
                        if k.name == 'Tax 5%':
                            kname= k.name
                            t5_tax += (i.price_subtotal_incl- i.price_subtotal)
                            t5t_tax += i.price_subtotal

                        if k.name == 'Tax 0%':
                            kname = k.name
                            t0_zerotax += i.price_subtotal

                        if k.name == 'Tax 28%':
                            kname = k.name
                            t28_tax += (i.price_subtotal_incl- i.price_subtotal)
                            t28t_tax += i.price_subtotal
                        if k.name == 'Tax 12%':
                            kname = k.name
                            t12_tax += (i.price_subtotal_incl- i.price_subtotal)
                            t12t_tax += i.price_subtotal
                        if k.name == 'Tax 18%':
                           t18_tax += (i.price_subtotal_incl- i.price_subtotal)
                           t18t_tax += i.price_subtotal
                           kname = k.name
                else:
                    t0_zerotax += i.price_subtotal

                res = {
                    'inv_id': j.id,
                    't_name': kname,
                    't0_amount': t0_zerotax ,
                    't5_amount': t5_tax,
                    't12_amount': t12_tax,
                    't18_amount': t18_tax,
                    't28_amount': t28_tax,
                    't5t_amount': t5t_tax,
                    't12t_amount': t12t_tax,
                    't18t_amount': t18t_tax,
                    't28t_amount': t28t_tax
                    }
                lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_lines(self, data):

        lines = []
        res = {}
        val = {}
        inv = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        company_id = data['form']['company_id']

        inv_ids = self.env["pos.order"].search([('date_order', '>=', date_start),
                                                ('date_order', '<=', date_end),
                                                ('company_id', '=', company_id),
                                                ('state', 'in', ['paid', 'posted','done'])]).sorted('date_order')

        tax_ids = self.env["account.tax"].search([])
        sl = 0

        for j in inv_ids:
            sl = sl + 1
            res = {
                'sl_no': sl,
                'inv_date': j.date_order,
                'c_name': j.partner_id.name,
                'c_address': j.partner_id.street,
                'inv_no': j.name,
                'c_gstin': j.partner_id.gst_in,
                'total': j.amount_total,
                'without_tax': j.amount_total-j.amount_tax,
                'inv_id': j.id,
                'c_type': 'Sale'

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

        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)

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
        sheet.set_column(21, 21, 20)
        sheet.set_column(22, 22, 20)


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

        sheet.merge_range('A1:B1', "GST Sales Report ", format1)
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
        sheet.write('I3', "Sales Total", blue_mark)
        sheet.write('J3', "With Out Tax", blue_mark)
        sheet.write('K3', "SALES-5%", blue_mark)
        sheet.write('L3', "S GST-2.5%", blue_mark)
        sheet.write('M3', "C GST-2.5%", blue_mark)
        sheet.write('N3', "SALES-12%", blue_mark)
        sheet.write('O3', "S GST-6%", blue_mark)
        sheet.write('P3', "C GST-6%", blue_mark)
        sheet.write('Q3', "SALES-18", blue_mark)
        sheet.write('R3', "S GST-9%", blue_mark)
        sheet.write('S3', "C GST-9%", blue_mark)
        sheet.write('T3', "SALES-28%", blue_mark)
        sheet.write('U3', "S GST-14%", blue_mark)
        sheet.write('V3', "C GST-14%", blue_mark)
        sheet.write('W3', "SALES-NonTaxble", blue_mark)
        # sheet.write('X3', "IGST", blue_mark)
        linw_row = 3

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['inv_date'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['c_name'], font_size_8)
            sheet.write(linw_row, line_column + 3, line['c_name'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['c_address'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['c_type'], font_size_8)
            sheet.write(linw_row, line_column + 6, line['inv_no'], font_size_8)
            sheet.write(linw_row, line_column + 7, line['c_gstin'], font_size_8)
            sheet.write_number(linw_row, line_column + 8, line['total'], font_size_8)
            sheet.write_number(linw_row, line_column + 9, line['without_tax'], font_size_8)
            for line2 in self.get_lines_two(data):

                if line2['t_name'] == 'Tax 5%' and line2['inv_id'] == line['inv_id']:
                    sheet.write_number(linw_row, line_column + 10, line2['t5t_amount'], font_size_8)
                    sheet.write_number(linw_row, line_column + 11, (line2['t5_amount']) / 2, font_size_8)
                    sheet.write_number(linw_row, line_column + 12, (line2['t5_amount']) / 2, font_size_8)

                if line2['t_name'] == 'Tax 12%' and line2['inv_id'] == line['inv_id']:
                    sheet.write_number(linw_row, line_column + 13, line2['t12t_amount'], font_size_8)
                    sheet.write_number(linw_row, line_column + 14, (line2['t12_amount']) / 2, font_size_8)
                    sheet.write_number(linw_row, line_column + 15, (line2['t12_amount']) / 2, font_size_8)

                if line2['t_name'] == 'Tax 18%' and line2['inv_id'] == line['inv_id']:
                    sheet.write_number(linw_row, line_column + 16, line2['t18t_amount'], font_size_8)
                    sheet.write_number(linw_row, line_column + 17, (line2['t18_amount']) / 2, font_size_8)
                    sheet.write_number(linw_row, line_column + 18, (line2['t18_amount']) / 2, font_size_8)

                if line2['t_name'] == 'Tax 28%' and line2['inv_id'] == line['inv_id']:
                    sheet.write_number(linw_row, line_column + 19, line2['t28t_amount'], font_size_8)
                    sheet.write_number(linw_row, line_column + 20, (line2['t28_amount']) / 2, font_size_8)
                    sheet.write_number(linw_row, line_column + 21, (line2['t28_amount']) / 2, font_size_8)

                if line2['t_name'] == 'Tax 0%' and line2['inv_id'] == line['inv_id']:
                    sheet.write_number(linw_row, line_column + 22, line2['t0_amount'], font_size_8)

                # if line2['t_name'] == 'IGST' and line2['inv_id'] == line['inv_id']:
                #     sheet.write_number(linw_row, line_column + 23, line2['t_amount'], font_size_8)

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

        total_cell_range11 = xl_range(3, 5, linw_row - 1, 5)
        total_cell_range = xl_range(3, 7, linw_row - 1, 7)
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
        total_cell_range18 = xl_range(3, 18, linw_row - 1, 18)
        total_cell_range19 = xl_range(3, 19, linw_row - 1, 19)
        total_cell_range20 = xl_range(3, 20, linw_row - 1, 20)
        total_cell_range21 = xl_range(3, 21, linw_row - 1, 21)
        total_cell_range22 = xl_range(3, 22, linw_row - 1, 22)
        total_cell_range23 = xl_range(3, 23, linw_row - 1, 23)
        sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range + ')', format1)
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
        sheet.write_formula(linw_row, 18, '=SUM(' + total_cell_range18 + ')', format1)
        sheet.write_formula(linw_row, 19, '=SUM(' + total_cell_range19 + ')', format1)
        sheet.write_formula(linw_row, 20, '=SUM(' + total_cell_range20 + ')', format1)
        sheet.write_formula(linw_row, 21, '=SUM(' + total_cell_range21 + ')', format1)
        sheet.write_formula(linw_row, 22, '=SUM(' + total_cell_range22 + ')', format1)
        # sheet.write_formula(linw_row, 23, '=SUM(' + total_cell_range23 + ')', format1)
Gst_posale_Reg_Xls('report.gst_posale_reg_xls.income_posale_xls.xlsx', 'account.invoice')
