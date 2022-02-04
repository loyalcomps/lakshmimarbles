from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from odoo.tools.translate import _


class TakeFastSlow(ReportXlsx):



    def get_sale(self, data):

        lines = []
        line = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        slow_move = data['form']['slow_move']
        ware_house = data['form']['store_id']
        if slow_move==False:
            query = '''
                        SELECT max(pol.id) AS id,
                        max(pol.product_id) AS product_id,
                        sl.name as stockname,
                        pt.name as product,
                        pp.barcode as itemcode,
                        pt.list_price as sale_price,
                        max(po.company_id) AS company_id,
                        max('Point of Sale') AS origin,
                        sum(pol.qty) AS qty,
                        sum(pol.price_unit * pol.qty * (1 - (pol.discount) / 100.0)) as total
                        FROM pos_order_line pol
                        INNER JOIN product_product pp ON pp.id = pol.product_id
                        INNER JOIN pos_order po ON po.id = pol.order_id
                        inner join stock_location sl on po.location_id=sl.id
                        inner join product_template pt on pt.id=pol.product_id   
                        left join stock_warehouse wh on (wh.lot_stock_id=po.location_id)
                        where to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date 
                        between %s and %s   and wh.id=%s and  po.state IN ('done', 'paid', 'invoiced') 
                        and (not pt.name='Discount')
                        Group by pt.name,sl.name,pp.barcode,pt.list_price order by qty desc
                        '''
        else:

            query = '''  SELECT max(pol.id) AS id,
                                    max(pol.product_id) AS product_id,
                                    sl.name as stockname,
                                    pt.name as product,
                                    pp.barcode as itemcode,
                                    pt.list_price as sale_price,
                                    max(po.company_id) AS company_id,
                                    max('Point of Sale') AS origin,
                                    sum(pol.qty) AS qty,
                                    sum(pol.price_unit * pol.qty * (1 - (pol.discount) / 100.0)) as total
                                    FROM pos_order_line pol
                                    INNER JOIN product_product pp ON pp.id = pol.product_id
                                    INNER JOIN pos_order po ON po.id = pol.order_id
                                    inner join stock_location sl on po.location_id=sl.id
                                    inner join product_template pt on pt.id=pol.product_id   
                                    left join stock_warehouse wh on (wh.lot_stock_id=po.location_id)

                                    where 
                                    to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date 
                                     between %s and %s   and wh.id=%s  and po.state IN ('done', 'paid', 'invoiced') 
                                    and (not pt.name='Discount')
                                   Group by pt.name,sl.name,pp.barcode,pt.list_price order by qty asc'''
        self.env.cr.execute(query,(date_start,date_end,(tuple(ware_house))))
        line = self.env.cr.dictfetchall()
        if line:
            return line
        else:
            return {}
        # pos_order_line = self.env['pos.order.line'].search([
        #     ('order_id.date_order','>=',date_start),
        #     ('order_id.date_order', '<=', date_end),
        #     ('company_id', '=', company_id),
        #     ('order_id.state', 'in', ['paid', 'invoiced', 'done'])])
        # product = {}
        # for line in pos_order_line:
        #     res = {
        #         'product':line.product_id.name,
        #         'category':line.product_id.category_id.name,
        #         'sale_price':line.price_unit,
        #         'qty':line.qty,
        #         'total':line.price_subtotal_incl
        #     }
        #     if line.product_id.id not in product:
        #         product[line.product_id.id]=res
        #     else:
        #         product[line.product_id.id]['sale_price']+=res['sale_price']
        #         product[line.product_id.id]['qty'] += res['qty']
        #         product[line.product_id.id]['total'] += res['total']
        #
        #
        # lines.append(product)
        #
        # if lines:
        #     return lines
        # else:
        #     return []



    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Fast/Slow Move Sales Report'))
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
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 20, 'bold': True,
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

        sheet.merge_range('A1:B1', "Fast/Slow Move Sales Report ", format1)
        sheet.write('C1', "DATE :-", format1)
        sheet.merge_range('D1:E1', date_start + ' - ' + date_end, format1)

        sheet.write('A3', "Product", blue_mark)
        sheet.write('B3', "Barcode", blue_mark)
        sheet.write('C3', "TRP", blue_mark)
        sheet.write('D3', "Quantity ", blue_mark)
        sheet.write('E3', "Total", blue_mark)

        line_row = 3
        line_column = 0
        for line in self.get_sale(data):
            sheet.write(line_row, line_column , line['product'], font_size_8)
            sheet.write(line_row, line_column + 1, line['itemcode'], font_size_8)
            sheet.write(line_row, line_column + 2, line['sale_price'], font_size_8)
            sheet.write(line_row, line_column + 3, line['qty'], font_size_8)
            sheet.write_number(line_row, line_column + 4, line['total'], font_size_8)

            line_row = line_row + 1
            line_column = 0
        sheet.write(line_row, 0, "TOTAL", green_mark)
        total_cell_range1 = xl_range(3, 4, line_row - 1, 4)

        sheet.write_formula(line_row, 4, '=SUM(' + total_cell_range1 + ')', format1)


TakeFastSlow('report.take_fastslowmove_xls.take_fastslow_xls.xlsx', 'sale.order')
