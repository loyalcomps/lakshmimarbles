from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime


class writeOff(ReportXlsx):

    def get_product(self, data):

        lines = []
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']
        product_id = data['form']['product_id']

        query = '''select pp.barcode,pt.name,sm.onhand_qty,(sm.onhand_qty*sm.price_unit) as value,
                    sm.product_uom_qty as scrap_qty,(sm.product_uom_qty*sm.price_unit) as scrap_value,
                    (sm.onhand_qty-sm.product_uom_qty) as ext_qty, 
                    ((sm.onhand_qty-sm.product_uom_qty)*sm.price_unit) as ext_value from stock_move sm
                    left join product_product as pp on pp.id=sm.product_id
                    left join product_template as pt on pt.id=pp.product_tmpl_id

                    where sm.scrapped= true and sm.location_id =%s and sm.company_id=%s and sm.state ='done'
                    and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date = %s and pp.id=%s'''

        sl = 0
        self.env.cr.execute(query, (stock_location, company_id, date_start,product_id))
        for row in self.env.cr.dictfetchall():
            sl += 1
            barcode = row['barcode'] if row['barcode'] else 0
            name = row['name'] if row['name'] else 0
            opening_stock = row['onhand_qty'] if row['onhand_qty'] else 0
            current_system_stock = row['value'] if row['value'] else 0
            trans_qty = row['scrap_qty'] if row['scrap_qty'] else 0
            trans_val = row['scrap_value'] if row['scrap_value'] else 0
            closing_stock = row['ext_qty'] if row['ext_qty'] else 0
            current_val = row['ext_value'] if row['ext_value'] else 0

            res = {
                'sl': sl,
                'barcode': barcode,
                'product': name,
                'opening_stock': round(opening_stock,2),
                'current_system_stock': round(current_system_stock,2),
                'transferred_qty': round(trans_qty,2),
                'transferred_value': round(trans_val,2),
                'current_value': round(current_val,2),
                'closing_stock': round(closing_stock,2),

            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []
    def get_product_location(self, data):

        lines = []
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']


        query= '''select pp.barcode,pt.name,sm.onhand_qty,(sm.onhand_qty*sm.price_unit) as value,
            sm.product_uom_qty as scrap_qty,(sm.product_uom_qty*sm.price_unit) as scrap_value,
            (sm.onhand_qty-sm.product_uom_qty) as ext_qty, 
            ((sm.onhand_qty-sm.product_uom_qty)*sm.price_unit) as ext_value from stock_move sm
            left join product_product as pp on pp.id=sm.product_id
            left join product_template as pt on pt.id=pp.product_tmpl_id

            where sm.scrapped= true and sm.location_id =%s and sm.company_id=%s and sm.state ='done'
            and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date = %s  '''

        sl = 0
        self.env.cr.execute(query, (stock_location,company_id,date_start))
        for row in self.env.cr.dictfetchall():
            sl+=1
            barcode = row['barcode'] if row['barcode'] else 0
            name = row['name'] if row['name'] else 0
            opening_stock = row['onhand_qty'] if row['onhand_qty'] else 0
            current_system_stock = row['value'] if row['value'] else 0
            trans_qty = row['scrap_qty'] if row['scrap_qty'] else 0
            trans_val = row['scrap_value'] if row['scrap_value'] else 0
            closing_stock = row['ext_qty'] if row['ext_qty'] else 0
            current_val = row['ext_value'] if row['ext_value'] else 0

            res = {
                'sl':sl,
                'barcode': barcode,
                'product': name,
                'opening_stock': round(opening_stock,2),
                'current_system_stock': round(current_system_stock,2),
                'transferred_qty': round(trans_qty,2),
                'transferred_value': round(trans_val,2) ,
                'current_value': round(current_val,2),
                'closing_stock': round(closing_stock,2),

            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_line(self, data):

        lines = []
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']
        category_id = data['form']['category_id']
        product_id = data['form']['product_id']

        cr = 0

        query = '''select pp.barcode,pt.name,sm.onhand_qty,(sm.onhand_qty*sm.price_unit) as value,
                            sm.product_uom_qty as scrap_qty,(sm.product_uom_qty*sm.price_unit) as scrap_value,
                            (sm.onhand_qty-sm.product_uom_qty) as ext_qty, 
                            ((sm.onhand_qty-sm.product_uom_qty)*sm.price_unit) as ext_value from stock_move sm
                            left join product_product as pp on pp.id=sm.product_id
                            left join product_template as pt on pt.id=pp.product_tmpl_id

                            where sm.scrapped= true and sm.location_id =%s and sm.company_id=%s and sm.state ='done'
                            and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date = %s and pp.id=%s and pt.categ_id=%s'''

        sl = 0
        self.env.cr.execute(query, (stock_location, company_id, date_start, product_id,category_id))
        for row in self.env.cr.dictfetchall():
            sl += 1
            barcode = row['barcode'] if row['barcode'] else 0
            name = row['name'] if row['name'] else 0
            opening_stock = row['onhand_qty'] if row['onhand_qty'] else 0
            current_system_stock = row['value'] if row['value'] else 0
            trans_qty = row['scrap_qty'] if row['scrap_qty'] else 0
            trans_val = row['scrap_value'] if row['scrap_value'] else 0
            closing_stock = row['ext_qty'] if row['ext_qty'] else 0
            current_val = row['ext_value'] if row['ext_value'] else 0

            res = {
                'sl': sl,
                'barcode': barcode,
                'product': name,
                'opening_stock': round(opening_stock,2),
                'current_system_stock': round(current_system_stock,2),
                'transferred_qty': round(trans_qty,2),
                'transferred_value': round(trans_val,2),
                'current_value': round(current_val,2),
                'closing_stock': round(closing_stock,2),

            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_product_category(self, data):

        lines = []

        date_start = data['form']['date_start']
        company_id = data['form']['company_id']
        stock_location = data['form']['stock_location']
        category_id = data['form']['category_id']

        query = '''select pp.barcode,pt.name,sm.onhand_qty,(sm.onhand_qty*sm.price_unit) as value,
                    sm.product_uom_qty as scrap_qty,(sm.product_uom_qty*sm.price_unit) as scrap_value,
                    (sm.onhand_qty-sm.product_uom_qty) as ext_qty, 
                    ((sm.onhand_qty-sm.product_uom_qty)*sm.price_unit) as ext_value from stock_move sm
                    left join product_product as pp on pp.id=sm.product_id
                    left join product_template as pt on pt.id=pp.product_tmpl_id
                    
                    where sm.scrapped= true and sm.location_id =%s and sm.company_id=%s and sm.state ='done'
                    and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date = %s  and pt.categ_id=%s'''

        sl = 0
        self.env.cr.execute(query, (stock_location, company_id, date_start,category_id))
        for row in self.env.cr.dictfetchall():
            sl += 1
            barcode = row['barcode'] if row['barcode'] else 0
            name = row['name'] if row['name'] else 0
            opening_stock = row['onhand_qty'] if row['onhand_qty'] else 0
            current_system_stock = row['value'] if row['value'] else 0
            trans_qty = row['scrap_qty'] if row['scrap_qty'] else 0
            trans_val = row['scrap_value'] if row['scrap_value'] else 0
            closing_stock = row['ext_qty'] if row['ext_qty'] else 0
            current_val = row['ext_value'] if row['ext_value'] else 0

            res = {
                'sl': sl,
                'barcode': barcode,
                'product': name,
                'opening_stock': round(opening_stock,2),
                'current_system_stock': round(current_system_stock,2),
                'transferred_qty': round(trans_qty,2),
                'transferred_value': round(trans_val,2),
                'current_value': round(current_val,2),
                'closing_stock': round(closing_stock,2),

            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Write Off Report'))
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

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        company_id = data['form']['company_id']
        date_start = data['form']['date_start']
        product_id = data['form']['product_id']
        category_id = data['form']['category_id']


        stock_location = data['form']['stock_location']
        stock_parent = self.env["stock.location"].browse(stock_location).location_id.name
        stock_name = self.env["stock.location"].browse(stock_location).name

        company = self.env['res.company'].browse(data['form']['company_id']).name
        company_address = self.env['res.company'].browse(data['form']['company_id']).street
        date_start = datetime.strptime(date_start, '%Y-%m-%d').date()


        sheet.merge_range('A1:I1', company, blue_mark3)
        sheet.merge_range('A2:I2', company_address, blue_mark2)
        sheet.merge_range('A3:I3', "Write Off Report ", blue_mark2)
        sheet.merge_range('A4:I4', date_start.strftime(
            '%d-%m-%Y'), blue_mark2)
        sheet.merge_range('A5:I5', "Location :- "+  stock_parent + stock_name, blue_mark24)
        # if category_id:
        #     sheet.merge_range('A6:I6', "Category :- " + stock_parent + stock_name, blue_mark24)

        sheet.write('A7', "Sl", blue_mark)
        sheet.write('B7', "Barcode", blue_mark)
        sheet.write('C7', "Product", blue_mark)

        sheet.write('D7', "Opening Stock Qty", blue_mark)
        sheet.write('E7', "Opening Stock Value", blue_mark)
        sheet.write('F7', "Transferred Qty", blue_mark)
        sheet.write('G7', "Transferred Value", blue_mark)
        sheet.write('H7', "Closing Stock Qty", blue_mark)
        sheet.write('I7', "Closing Stock Value", blue_mark)


        linw_row = 7

        line_column = 0


        if product_id == False and category_id == False:

            for line in self.get_product_location(data):
                sheet.write(linw_row, line_column, line['sl'], font_size_8)
                sheet.write(linw_row, line_column + 1, line['barcode'], font_size_8)
                sheet.write(linw_row, line_column + 2, line['product'], font_size_8)

                sheet.write(linw_row, line_column + 3, line['opening_stock'], font_size_8)
                sheet.write(linw_row, line_column + 4, line['current_system_stock'], font_size_8)
                sheet.write(linw_row, line_column + 5, line['transferred_qty'], font_size_8)
                sheet.write(linw_row, line_column + 6, line['transferred_value'], font_size_8)
                sheet.write(linw_row, line_column + 7, line['closing_stock'], font_size_8)
                sheet.write(linw_row, line_column + 8, line['current_value'], font_size_8)


                linw_row = linw_row + 1
                line_column = 0

            line_column = 0

            sheet.write(linw_row, 0, "TOTAL", format1)
            total_cell_range11 = xl_range(7, 7, linw_row - 1, 7)

            sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range11 + ')', format1)

            total_cell_range14 = xl_range(7, 8, linw_row - 1, 8)

            sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range14 + ')', format1)

        if product_id==False and category_id:


            for line in self.get_product_category(data):
                sheet.write(linw_row, line_column, line['sl'], font_size_8)
                sheet.write(linw_row, line_column + 1, line['barcode'], font_size_8)
                sheet.write(linw_row, line_column + 2, line['product'], font_size_8)

                sheet.write(linw_row, line_column + 3, line['opening_stock'], font_size_8)
                sheet.write(linw_row, line_column + 4, line['current_system_stock'], font_size_8)
                sheet.write(linw_row, line_column + 5, line['transferred_qty'], font_size_8)
                sheet.write(linw_row, line_column + 6, line['transferred_value'], font_size_8)
                sheet.write(linw_row, line_column + 7, line['closing_stock'], font_size_8)
                sheet.write(linw_row, line_column + 8, line['current_value'], font_size_8)




                linw_row = linw_row + 1
                line_column = 0

            line_column = 0



            sheet.write(linw_row, 0, "TOTAL", format1)
            total_cell_range11 = xl_range(7, 7, linw_row - 1, 7)

            sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range11 + ')', format1)

            total_cell_range14 = xl_range(7, 8, linw_row - 1, 8)

            sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range14 + ')', format1)

        if product_id and category_id == False:

            for line in self.get_product(data):
                sheet.write(linw_row, line_column, line['sl'], font_size_8)
                sheet.write(linw_row, line_column + 1, line['barcode'], font_size_8)
                sheet.write(linw_row, line_column + 2, line['product'], font_size_8)

                sheet.write(linw_row, line_column + 3, line['opening_stock'], font_size_8)
                sheet.write(linw_row, line_column + 4, line['current_system_stock'], font_size_8)
                sheet.write(linw_row, line_column + 5, line['transferred_qty'], font_size_8)
                sheet.write(linw_row, line_column + 6, line['transferred_value'], font_size_8)
                sheet.write(linw_row, line_column + 7, line['closing_stock'], font_size_8)
                sheet.write(linw_row, line_column + 8, line['current_value'], font_size_8)


                linw_row = linw_row + 1
                line_column = 0

            line_column = 0

            sheet.write(linw_row, 0, "TOTAL", format1)
            total_cell_range11 = xl_range(7, 7, linw_row - 1, 7)

            sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range11 + ')', format1)

            total_cell_range14 = xl_range(7, 8, linw_row - 1, 8)

            sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range14 + ')', format1)

        if product_id and category_id:


            for line in self.get_line(data):
                sheet.write(linw_row, line_column, line['sl'], font_size_8)
                sheet.write(linw_row, line_column + 1, line['barcode'], font_size_8)
                sheet.write(linw_row, line_column + 2, line['product'], font_size_8)

                sheet.write(linw_row, line_column + 3, line['opening_stock'], font_size_8)
                sheet.write(linw_row, line_column + 4, line['current_system_stock'], font_size_8)
                sheet.write(linw_row, line_column + 5, line['transferred_qty'], font_size_8)
                sheet.write(linw_row, line_column + 6, line['transferred_value'], font_size_8)
                sheet.write(linw_row, line_column + 7, line['closing_stock'], font_size_8)
                sheet.write(linw_row, line_column + 8, line['current_value'], font_size_8)


                linw_row = linw_row + 1
                line_column = 0

            line_column = 0

            sheet.write(linw_row, 0, "TOTAL", format1)
            total_cell_range11 = xl_range(7, 7, linw_row - 1, 7)

            sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range11 + ')', format1)

            total_cell_range14 = xl_range(7, 8, linw_row - 1, 8)

            sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range14 + ')', format1)


writeOff('report.write_off_report.writeoff_report_xls.xlsx', 'stock.inventory')
