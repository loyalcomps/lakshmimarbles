from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime


class taxwisereport(ReportXlsx):

    def get_cash(self, data):

        lines = []
        invoice_id = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']

        cr = 0

        query21 = '''
        Select
                        ROW_NUMBER() OVER(ORDER BY dd.date_invoice ASC) AS sl_no,
                        dd.date_invoice as date_invoice,
                        sum(dd.taxable) as total_taxable,
                        sum(dd.tax_amount) as total_tax,
                        sum(dd.total_am) as total,    

                     COALESCE(sum(CASE WHEN dd.tax=0 or dd.tax is null THEN dd.tax_amount ELSE 0 END ),0)  as tax0,
                    COALESCE(sum(CASE WHEN dd.tax=1 THEN dd.tax_amount ELSE 0 END ),0)  as tax1,
        	        COALESCE(sum(CASE dd.tax WHEN 5 THEN dd.tax_amount ELSE 0 END ),0)  as tax5,
                    COALESCE(sum(CASE  WHEN dd.tax = 12 THEN dd.tax_amount ELSE 0 END ),0)  as tax12,
                    COALESCE(sum(CASE dd.tax WHEN 18 THEN dd.tax_amount ELSE 0 END ),0)  as tax18,
                    COALESCE(sum(CASE dd.tax WHEN 28 THEN dd.tax_amount ELSE 0 END ),0)  as tax28,
                    COALESCE(sum(CASE dd.tax WHEN 40 THEN dd.tax_amount ELSE 0 END ),0)  as cesstax,

                    COALESCE(sum(CASE WHEN dd.tax=0 or dd.tax is null THEN dd.taxable ELSE 0 END ),0)  as taxable0,
                    COALESCE(sum(CASE WHEN dd.tax=1 THEN dd.taxable ELSE 0 END ),0)  as taxable1,
        	        COALESCE(sum(CASE dd.tax WHEN 5 THEN dd.taxable ELSE 0 END ),0)  as taxable5,
                    COALESCE(sum(CASE  WHEN dd.tax = 12 THEN dd.taxable ELSE 0 END ),0)  as taxable12,
                    COALESCE(sum(CASE dd.tax WHEN 18 THEN dd.taxable ELSE 0 END ),0)  as taxable18,
                    COALESCE(sum(CASE dd.tax WHEN 28 THEN dd.taxable ELSE 0 END ),0)  as taxable28,
                    COALESCE(sum(CASE dd.tax WHEN 40 THEN dd.taxable ELSE 0 END ),0)  as cesstaxable,

                     COALESCE(sum(CASE WHEN dd.tax=0 or dd.tax is null THEN dd.total_am ELSE 0 END ),0)  as sale0,
                    COALESCE(sum(CASE WHEN dd.tax=1 THEN dd.total_am ELSE 0 END ),0)  as sale1,
        	        COALESCE(sum(CASE dd.tax WHEN 5 THEN dd.total_am ELSE 0 END ),0)  as sale5,
                    COALESCE(sum(CASE  WHEN dd.tax = 12 THEN dd.total_am ELSE 0 END ),0)  as sale12,
                    COALESCE(sum(CASE dd.tax WHEN 18 THEN dd.total_am ELSE 0 END ),0)  as sale18,
                    COALESCE(sum(CASE dd.tax WHEN 28 THEN dd.total_am ELSE 0 END ),0)  as sale28,
                    COALESCE(sum(CASE dd.tax WHEN 40 THEN dd.total_am ELSE 0 END ),0)  as cesssale



                    from
                    (select ai.date_invoice,ai.number,ai.reference,
                    round(ai.amount_untaxed,2) as total_taxable,round(ai.amount_tax,2) as total_tax,
                    round(ai.amount_total,2) as total,
                    round(sum((CASE WHEN ai.type = 'out_refund'  then  -1*ail.price_subtotal ELSE ail.price_subtotal END)),2) as taxable,

                    round(sum(CASE WHEN ai.type = 'out_refund'  then  -1*ail.price_subtotal_taxinc ELSE ail.price_subtotal_taxinc END),2) as total_am,
                    round(sum((CASE WHEN ai.type = 'out_refund'  then  -1*ail.price_subtotal_taxinc ELSE ail.price_subtotal_taxinc END)-
                    (CASE WHEN ai.type = 'out_refund'  then  -1*ail.price_subtotal ELSE ail.price_subtotal END)),2) as tax_amount,at.amount as tax
                    from account_invoice as ai
                    left join account_invoice_line as ail on ail.invoice_id = ai.id
                    left join account_invoice_line_tax as ailt
                    on ailt.invoice_line_id=ail.id
                    left join account_tax as at
                    on at.id = ailt.tax_id
                    left join stock_location as sl
                    on (ai.stock_locations=sl.id) 

                    where ai.date_invoice BETWEEN %s and %s and sl.id=%s and
                    ai.state in ('open','paid')  and ai.type in ('out_invoice','out_refund')  
                    group by at.id,ai.id)dd
                    group by dd.date_invoice

                                                                                       '''

        self.env.cr.execute(query21, (date_start, date_end, stock_location))
        for row in self.env.cr.dictfetchall():
            # sl = sl + 1

            sale = 0
            possale = 0
            purtotal = 0

            # poscost = row['poscost'] if row['poscost'] else 0
            date_invoice = row['date_invoice'] if row['date_invoice'] else 0
            total_taxable = row['total_taxable'] if row['total_taxable'] else 0

            tax0 = row['tax0'] if row['tax0'] else 0
            tax1 = row['tax1'] if row['tax1'] else 0
            tax5 = row['tax5'] if row['tax5'] else 0
            tax12 = row['tax12'] if row['tax12'] else 0
            tax18 = row['tax18'] if row['tax18'] else 0
            tax28 = row['tax28'] if row['tax28'] else 0
            cesstax = row['cesstax'] if row['cesstax'] else 0

            sale0 = row['sale0'] if row['sale0'] else 0
            sale1 = row['sale1'] if row['sale1'] else 0
            sale5 = row['sale5'] if row['sale5'] else 0
            sale12 = row['sale12'] if row['sale12'] else 0
            sale18 = row['sale18'] if row['sale18'] else 0
            sale28 = row['sale28'] if row['sale28'] else 0
            cesssale = row['cesssale'] if row['cesssale'] else 0

            taxable0 = row['taxable0'] if row['taxable0'] else 0
            taxable1 = row['taxable1'] if row['taxable1'] else 0
            taxable5 = row['taxable5'] if row['taxable5'] else 0
            taxable12 = row['taxable12'] if row['taxable12'] else 0
            taxable18 = row['taxable18'] if row['taxable18'] else 0
            taxable28 = row['taxable28'] if row['taxable28'] else 0
            cesstaxable = row['cesstaxable'] if row['cesstaxable'] else 0

            total_tax = row['total_tax'] if row['total_tax'] else 0
            total = row['total'] if row['total'] else 0
            total_taxable = row['total_taxable'] if row['total_taxable'] else 0

            res = {
                'cesstaxable': cesstaxable,
                'cesssale': cesssale,
                'cesstax': cesstax,
                'date_invoice': date_invoice,
                'total_taxable': total_taxable,
                'sale0': sale0,
                'sale1': sale1,
                'sale5': sale5,
                'sale12': sale12,
                'sale18': sale18,
                'sale28': sale28,

                'taxable0': taxable0,
                'taxable1': taxable1,
                'taxable5': taxable5,
                'taxable12': taxable12,
                'taxable18': taxable18,
                'taxable28': taxable28,

                'tax0': tax0,
                'tax1': tax1,
                'tax5': tax5,
                'tax12': tax12,
                'tax18': tax18,
                'tax28': tax28,

                'total_tax': total_tax,
                'total': total,
                'total_taxable': total_taxable,

                # 'sl_no': sl,

            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []


    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Tax Report'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 20)
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
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']
        stock_parent = self.env["stock.location"].browse(stock_location).location_id.name
        stock_name = self.env["stock.location"].browse(stock_location).name


        # vendor_name = self.env["res.partner"].browse(vendor_id).name

        company = self.env['res.company'].browse(data['form']['company_id']).name
        #
        company_address = self.env['res.company'].browse(data['form']['company_id']).street

        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True})

        format11 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
             'bold': True})
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

        blue_mark2 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca', 'align': 'center'})
        blue_mark24 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca', 'align': 'left'})

        blue_mark3 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 18, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca', 'align': 'center'})

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        # if brand_id:

        sheet.merge_range('A1:P1', company, blue_mark3)
        sheet.merge_range('A2:P2', company_address, blue_mark2)
        sheet.merge_range('A3:P3', "Tax Report ", blue_mark2)
        sheet.merge_range('A4:P4', 'From ' + date_object_date_start.strftime(
            '%d-%m-%Y') + ' - To ' + date_object_date_end.strftime('%d-%m-%Y'), blue_mark2)
        sheet.merge_range('A5:P5', "Location :- "+  stock_parent + stock_name, blue_mark24)

        sheet.write('A7', "Date", blue_mark)
        sheet.write('B7', "Non-Tax Sales", blue_mark)

        sheet.write('C7', "Sales 1%", blue_mark)
        sheet.write('D7', "Tax 1%", blue_mark)
        sheet.write('E7', "sale 5%", blue_mark)
        sheet.write('F7', "Tax 5%", blue_mark)
        sheet.write('G7', "Sales 12%", blue_mark)
        sheet.write('H7', "Tax 12%", blue_mark)
        sheet.write('I7', "sale 18%", blue_mark)
        sheet.write('J7', "Tax 18%", blue_mark)
        sheet.write('K7', "Sales 28%", blue_mark)
        sheet.write('L7', "Tax 28%", blue_mark)
        sheet.write('M7', "Sale (GST 28% + Cess 12%)", blue_mark)
        sheet.write('N7', "Tax (GST 28% + Cess 12%)", blue_mark)
        sheet.write('O7', "Total Sales", blue_mark)
        sheet.write('P7', "Total Tax", blue_mark)
        # sheet.write('G7', "Profit", blue_mark)

        # config = self.env['product.brand'].browse(brand_only)
        # for pfg in config:

        linw_row = 7

        line_column = 0


        for line in self.get_cash(data):
            sheet.write(linw_row, line_column, line['date_invoice'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['taxable0'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['taxable1'], font_size_8)

            sheet.write(linw_row, line_column + 3, line['tax1'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['taxable5'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['tax5'], font_size_8)
            sheet.write(linw_row, line_column + 6, line['taxable12'], font_size_8)
            sheet.write(linw_row, line_column + 7, line['tax12'], font_size_8)
            sheet.write(linw_row, line_column + 8, line['taxable18'], font_size_8)
            sheet.write(linw_row, line_column + 9, line['tax18'], font_size_8)
            sheet.write(linw_row, line_column + 10, line['taxable28'], font_size_8)
            sheet.write(linw_row, line_column + 11, line['tax28'], font_size_8)

            sheet.write(linw_row, line_column + 12, line['cesstaxable'], font_size_8)
            sheet.write(linw_row, line_column + 13, line['cesstax'], font_size_8)
            sheet.write(linw_row, line_column + 14, line['total_taxable'], font_size_8)
            sheet.write(linw_row, line_column + 15, line['total_tax'], font_size_8)
            # sheet.write(linw_row, line_column + 6, line['profit'], font_size_8)

            linw_row = linw_row + 1
            line_column = 0

        line_column = 0



        sheet.write(linw_row, 0, "TOTAL", format1)

        total_cell_range12 = xl_range(3, 3, linw_row - 1, 3)
        total_cell_range11 = xl_range(3, 4, linw_row - 1, 4)
        total_cell_range = xl_range(3, 5, linw_row - 1, 5)
        total_cell_range_one = xl_range(3, 6, linw_row - 1, 6)

        total_cell_range13 = xl_range(3, 7, linw_row - 1, 7)
        total_cell_range14 = xl_range(3, 8, linw_row - 1, 8)
        total_cell_range15 = xl_range(3, 9, linw_row - 1, 9)
        total_cell_range16 = xl_range(3, 10, linw_row - 1, 10)

        total_cell_range17 = xl_range(3, 11, linw_row - 1, 11)
        total_cell_range18 = xl_range(3, 12, linw_row - 1, 12)
        total_cell_range19 = xl_range(3, 13, linw_row - 1, 13)
        total_cell_range21 = xl_range(3, 14, linw_row - 1, 14)
        total_cell_range22 = xl_range(3, 15, linw_row - 1, 15)
        total_cell_range20 = xl_range(3, 2, linw_row - 1, 2)
        total_cell_range25 = xl_range(3, 1, linw_row - 1, 1)
        # total_cell_range_three = xl_range(3, 6, linw_row - 1, 6)

        sheet.write_formula(linw_row, 3, '=SUM(' + total_cell_range12 + ')', format1)
        sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 5, '=SUM(' + total_cell_range + ')', format1)
        sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_one + ')', format1)

        sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range13 + ')', format1)
        sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range14 + ')', format1)
        sheet.write_formula(linw_row, 9, '=SUM(' + total_cell_range15 + ')', format1)
        sheet.write_formula(linw_row, 10, '=SUM(' + total_cell_range16 + ')', format1)

        sheet.write_formula(linw_row, 11, '=SUM(' + total_cell_range17 + ')', format1)
        sheet.write_formula(linw_row, 12, '=SUM(' + total_cell_range18 + ')', format1)
        sheet.write_formula(linw_row, 13, '=SUM(' + total_cell_range19 + ')', format1)
        sheet.write_formula(linw_row, 2, '=SUM(' + total_cell_range20 + ')', format1)
        sheet.write_formula(linw_row, 14, '=SUM(' + total_cell_range21 + ')', format1)
        sheet.write_formula(linw_row, 15, '=SUM(' + total_cell_range22 + ')', format1)
        sheet.write_formula(linw_row, 1, '=SUM(' + total_cell_range25 + ')', format1)

        # sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_three + ')', format1)


taxwisereport('report.daily_tax_report.qlty_sale_report_xls.xlsx', 'sale.order')
