from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _


class QltyCategory(ReportXlsx):



    def get_lines(self, data):

        lines = []



        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        category_id = data['form']['category_id']

        if category_id:
            sale_lines = self.env["pos.order.line"].search(
                [('order_id.date_order', '>=', date_start), ('order_id.date_order', '<=', date_end),
                 ('company_id', '=', company_id), ('product_id.category_id', '=', category_id),
                 ('order_id.state', 'in', ['done', 'paid', 'invoiced'])])

            out_invoice_lines = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('invoice_id.type', '=', 'out_invoice'),
                 ('product_id.category_id', '=', category_id),
                 ('invoice_id.state', 'in', ['open', 'paid'])])

            query1 = '''select * from account_invoice_line as ai
                    left join account_invoice as a
                    on a.id=ai.invoice_id
                    left join product_product as p
                    on ai.product_id =p.id
                    left join pdct_category as pc
                    on p.category_id =pc.id
                    where a.type='in_invoice' and a.state in ('open','paid') and p.category_id = %s'''


            purchase_lines = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('product_id.category_id', '=', category_id), ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])
            product = self.env["product.product"].search([('category_id', '=', category_id)])
        else:
            sale_lines = self.env["pos.order.line"].search(
                [('order_id.date_order', '>=', date_start), ('order_id.date_order', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('order_id.state', 'in', ['done', 'paid', 'invoiced'])])
            out_invoice_lines = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id), ('invoice_id.type', '=', 'out_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])

            purchase_lines_total = self.env["account.invoice.line"].search(
                [('company_id', '=', company_id),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])

            purchase_lines = self.env["account.invoice.line"].search([('invoice_id.type', '=', 'in_invoice'),
                                                                      ('invoice_id.date_invoice', '>=', date_start),
                                                                      ('invoice_id.date_invoice', '<=', date_end),
                                                                      ('company_id', '=', company_id),
                                                                      ('invoice_id.state', 'in', ['open', 'paid'])])
            product = self.env["product.product"].search([])

        sl=0
        for i in product:
            s_amt = 0
            s_qty = 0
            p_qty = 0
            profit = 0
            p_amt = 0
            sl += 1
            sale_query = ''' select SUM(ai.quantity) as sale_qty,SUM(ai.price_subtotal_taxinc) as sale_amount,product_id from account_invoice_line as ai
                left join account_invoice as a
                on a.id=ai.invoice_id
                left join product_product as p
                on ai.product_id =p.id
                left join pdct_category as pc
                on p.category_id =pc.id
                where a.type='out_invoice' and a.state in ('open','paid') and
                p.id = %s and a.company_id = %s and a.date_invoice BETWEEN %s and %s
                GROUP BY ai.product_id'''
            self.env.cr.execute(sale_query, (i.id, company_id,date_start,date_end,))
            for row in self.env.cr.dictfetchall():
                s_amt += row['sale_qty'] if row['sale_qty'] else 0
                s_qty += row['sale_amount'] if row['sale_amount'] else 0

            pos_query = ''' select SUM(ai.qty) as sale_qty,SUM(round(((ai.qty * ai.price_unit) - ai.discount),2) ) as sale_amount,product_id from pos_order_line as ai
                left join pos_order as a
                on a.id=ai.order_id
                left join product_product as p
                on ai.product_id =p.id
                left join pdct_category as pc
                on p.category_id =pc.id
                where  a.state in ('done','paid')  and
                            p.id = %s and a.company_id = %s and a.date_order BETWEEN %s and %s
                            GROUP BY ai.product_id'''
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            start_date = datetime.datetime.strptime(date_start + ' 00:00:00', DATETIME_FORMAT)
            end_date = datetime.datetime.strptime(date_end + ' 00:00:00', DATETIME_FORMAT)
            self.env.cr.execute(pos_query, (i.id, company_id,start_date,end_date))
            for row in self.env.cr.dictfetchall():
                s_amt += row['sale_qty'] if row['sale_qty'] else 0
                s_qty += row['sale_amount'] if row['sale_amount'] else 0

            average_cost_query = '''select SUM(ai.price_subtotal_taxinc/ai.quantity) as average_cost from account_invoice_line as ai
            left join account_invoice as a
            on a.id=ai.invoice_id
            left join product_product as p
            on ai.product_id =p.id
            left join pdct_category as pc
            on p.category_id =pc.id
            where a.type='in_invoice' and a.state in ('open','paid') and p.id = %s and a.company_id = %s
            '''
            self.env.cr.execute(average_cost_query,(i.id,company_id,))
            for row in self.env.cr.dictfetchall():

                average_cost = row['average_cost'] if row['average_cost'] else 0
            purchase_query = ''' select SUM(ai.quantity) as purchase_qty,SUM(ai.price_subtotal_taxinc) as purchase_amount,product_id from account_invoice_line as ai
                left join account_invoice as a
                on a.id=ai.invoice_id
                left join product_product as p
                on ai.product_id =p.id
                left join pdct_category as pc
                on p.category_id =pc.id
                where a.type='in_invoice' and a.state in ('open','paid') and
                            p.id = %s and a.company_id = %s and a.date_invoice BETWEEN %s and %s
                            GROUP BY ai.product_id'''
            self.env.cr.execute(purchase_query, (i.id, company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                p_qty += row['purchase_qty'] if row['purchase_qty'] else 0
                p_amt += row['purchase_amount'] if row['purchase_amount'] else 0


            # for j in sale_lines:
            #     if i.id == j.product_id.id:
            #         s_amt += j.price_subtotal_incl
            #         s_qty += j.qty

            # for k in purchase_lines:
            #     if i.id == k.product_id.id:
            #         p_amt += k.price_subtotal_taxinc
            #         p_qty += k.quantity
            # for l in out_invoice_lines:
            #     if i.id == l.product_id.id:
            #         s_amt += l.price_subtotal_taxinc
            #         s_qty += l.quantity

            res = {
                'sl_no': sl,
                'product': i.name,
                'category': i.category_id.name,
                'onhand': i.qty_available,
                's_qty': s_qty,
                'sale': s_amt,
                'p_qty': p_qty,
                'purchase': p_amt,
                'profit': round((s_amt-(average_cost*s_qty)),2)
            }

            lines.append(res)




        if lines:
            return lines
        else:
            return []






    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Product'))
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
        category_id = data['form']['category_id']

        category_name = self.env["pdct.category"].browse(category_id).name

        company=self.env['res.company'].browse(data['form']['company_id']).name

        company_address=self.env['res.company'].browse(data['form']['company_id']).street


        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True})

        format2 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center', 'bold': True})

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

        # sheet.merge_range('A1:B1', "Category Wise Report ", format1)
        # sheet.write('C1', category_name, format1)
        # sheet.write('D1', "DATE :-", format1)
        # sheet.merge_range('E1:F1', date_start + ' - ' + date_end, format1)


        sheet.merge_range('C1:F1', company, format2)
        sheet.merge_range('C2:F2', company_address,format2)
        sheet.merge_range('C3:F3', "Category Wise Report",format2)
        sheet.merge_range('C4:F4', date_start + '-' + date_end, format2)
        sheet.merge_range('C5:F5', category_name,format2)




        sheet.write('A6', "Sl No", blue_mark)
        sheet.write('B6', "Product", blue_mark)
        sheet.write('C6', "Category", blue_mark)
        sheet.write('D6', "Purchased Qty", blue_mark)
        sheet.write('E6', "Purchase ", blue_mark)
        sheet.write('F6', "Saled Qty ", blue_mark)
        sheet.write('G6', "Sale", blue_mark)
        sheet.write('H6', "Onhand", blue_mark)
        sheet.write('I6', "Profit", blue_mark)
        # sheet.write('J3', "With Out Tax", blue_mark)
        # sheet.write('K3', "SALES-5%", blue_mark)
        # sheet.write('L3', "S GST-2.5%", blue_mark)
        # sheet.write('M3', "C GST-2.5%", blue_mark)
        # sheet.write('N3', "SALES-12%", blue_mark)
        # sheet.write('O3', "S GST-6%", blue_mark)
        # sheet.write('P3', "C GST-6%", blue_mark)
        # sheet.write('Q3', "SALES-18", blue_mark)
        # sheet.write('R3', "S GST-9%", blue_mark)
        # sheet.write('S3', "C GST-9%", blue_mark)
        # sheet.write('T3', "SALES-28%", blue_mark)
        # sheet.write('U3', "S GST-14%", blue_mark)
        # sheet.write('V3', "C GST-14%", blue_mark)
        # sheet.write('W3', "SALES-NonTaxble", blue_mark)
        # sheet.write('X3', "IGST", blue_mark)
        linw_row = 6

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['product'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['category'], font_size_8)
            sheet.write(linw_row, line_column + 3, line['p_qty'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['purchase'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['s_qty'], font_size_8)
            sheet.write(linw_row, line_column + 6, line['sale'], font_size_8)
            sheet.write(linw_row, line_column + 7, line['onhand'], font_size_8)
            sheet.write_number(linw_row, line_column + 8, line['profit'], font_size_8)
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

        sheet.write(linw_row, 0, "TOTAL", format1)

        total_cell_range11 = xl_range(3, 6, linw_row - 1, 6)
        total_cell_range = xl_range(3, 8, linw_row - 1, 8)
        total_cell_range_one = xl_range(3, 4, linw_row - 1, 4)
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


        sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range + ')', format1)
        sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range_one + ')', format1)
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


QltyCategory('report.qlty_categorywise_xls.qlty_category_xls.xlsx', 'sale.order')
