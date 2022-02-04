from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from odoo.tools.translate import _
import dateutil.parser

class seveninventoryXls(ReportXlsx):

    def get_lines(self, data):

        lines = []
        res = {}
        val = {}
        inv = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        wh_id = data['form']['wh_id']
        min_qty = data['form']['min_qty']
        sl = 0

        query = '''  select (pp.id),pp.barcode as barcode,pp.brand_id as brand,sum(sh.quantity) as qty,pt.list_price as sale_price,
sum(sh.quantity)*pt.list_price as tamount,
max(pt.name) as product,max(pb.name) as brandname from product_product as pp
		left join stock_history as sh on(pp.id=sh.product_id)
		left join product_template pt on (pt.id=pp.product_tmpl_id)
		left join product_brand as pb on (pb.id=pp.brand_id) 
             
 where 
 sh.quantity>0 and
 pp.id not in(select pol.product_id from pos_order_line as pol
					left join pos_order as po on(po.id=pol.order_id)
					left join product_product as pp on (pp.id=pol.product_id)
					left join product_template as pt on (pt.id=pp.product_tmpl_id)

					where to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date 
                            between %s and %s and  po.state IN ('done', 'paid', 'invoiced') 
				and po.company_id=%s group by pol.product_id
					) group by pp.id,pt.list_price,pt.name order by pt.name ASC

                                '''
        self.env.cr.execute(query, (date_start, date_end, company_id))

        for row in self.env.cr.dictfetchall():
            sl += 1
            productname = row['product'] if row['product'] else 0
            quantity = row['qty'] if row['qty'] else 0
            barcode = row['barcode'] if row['barcode'] else 0
            brand = row['brandname'] if row['brandname'] else 0
            sale_price = row['sale_price'] if row['sale_price'] else 0
            tamount = row['tamount'] if row['tamount'] else 0
            sl += 1

            res = {



                'sl_no': sl if sl else 0,

                'product': productname,
                # 'quantity': quantity,
                'barcode': barcode,
                'brand': brand,
                'qty': quantity,
                'trp': sale_price,
                'total': tamount,

            }
            lines.append(res)

        if lines:

            return lines
        else:
            return []



    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Deadstock Report'))
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

        sheet.merge_range('A1:B1', "Ageing Products Report", format1)
        sheet.write('C1', "DATE :-", format1)
        sheet.merge_range('D1:E1', date_start + ' - ' + date_end, format1)

        sheet.write('A3', "Product", blue_mark)
        sheet.write('B3', "Barcode", blue_mark)
        sheet.write('C3', "Brand", blue_mark)
        sheet.write('D3', "ORP", blue_mark)
        # sheet.write('E3', "TRP", blue_mark)
        # sheet.write('F3', "Total", blue_mark)

        linw_row = 3

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['product'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['barcode'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['brand'], font_size_8)
            # sheet.write(linw_row, line_column + 3, line['qty'], font_size_8)
            sheet.write(linw_row, line_column + 3, line['trp'], font_size_8)
            # sheet.write(linw_row, line_column + 5, line['total'], font_size_8)



            linw_row = linw_row + 1
            line_column = 0

        line_column = 0



        # sheet.write(linw_row, 0, "TOTAL", format1)
        #
        # total_cell_range11 = xl_range(3, 3, linw_row - 1, 3)
        # # total_cell_range12 = xl_range(3, 4, linw_row - 1, 4)
        # # total_cell_range = xl_range(3, 5, linw_row - 1, 5)
        #
        #
        # sheet.write_formula(linw_row, 3, '=SUM(' + total_cell_range11 + ')', format1)
        # sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range12 + ')', format1)
        # sheet.write_formula(linw_row, 5, '=SUM(' + total_cell_range + ')', format1)



seveninventoryXls('report.seven_deadstock_xls.seven_deadstock_xls.xlsx', 'product.product')
