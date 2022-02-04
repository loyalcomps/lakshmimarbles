from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime


class Ainventory_pdf(ReportXlsx):

    def get_lines(self, data):
        lines = []
        sl = 0
        product = []
        average_cost = 0
        date_start = data['form']['date_start']

        company_id = data['form']['company_id']

        query1 = """select
            dd.id as id,dd.pname as pname,
            dd.catname as catname,
            dd.sale_date as sale_date,
            dd.pur_date as pur_date,
            dd.onhand as onhand,
           dd.mrp as mrp,dd.list_price as list_price,dd.costp as cost
            
             from (

 (select sh.product_id as id ,max(pt.name) as pname,
    			  pt.product_mrp as mrp ,pt.list_price as list_price,
    			  COALESCE(sum(sh.quantity),0)  as onhand ,
    			  max(pc.name) as catname
    			  
    			  from stock_history as sh
             left join product_product as pp on(pp.id=sh.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
             left join product_category pc on (pc.id=sh.product_categ_id)

             where to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date <=%s
             
              group by sh.product_id,pt.id having sum(sh.quantity)<0 order by pname 
                 ) a 





                 
                                            left join
            (
            select aal.product_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale,
            max(aa.date_invoice) as sale_date
             from
            account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
    	 left join product_product as pp on(pp.id=aal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
            where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice <=%s
            and  aa.company_id= %s
           group by aal.product_id
           ) b
                                          on a.id=b.product_id
                                          left join
            (
            select aaal.product_id ,sum(aaal.price_subtotal) as pur_total,max(aaa.date_invoice) as pur_date from
            account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
            where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice <=%s
            and  aaa.company_id= %s
    	group by aaal.product_id
    	) c
            on a.id=c.product_id
            
            left join

            (

select aaal.product_id,
max(aaal.price_unit) as costp from 
	account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)

              where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid')
               and aaa.date_invoice <=%s and aaal.invoice_id in
             (select max(aaal.invoice_id) from 
account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
            where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice <=%s 
            and aaa.date_invoice in (select max(aaa.date_invoice) from account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    	left join product_product as pp on(pp.id=aaal.product_id)
             left join product_template pt on (pt.id=pp.product_tmpl_id)
            where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') 
            and aaa.date_invoice <=%s group by  aaal.product_id) 
            group by aaal.product_id )group by aaal.product_id


            )d on a.id=d.product_id



            ) as dd order by dd.pname

    """

        self.env.cr.execute(query1, (date_start,
                                     date_start,company_id,
                                        date_start,company_id,date_start,date_start,date_start,

                                     ))

        for row in self.env.cr.dictfetchall():

            sl+=1
            sale = 0
            possale = 0
            purtotal = 0
            pname = row['pname'] if row['pname'] else 0
            catname = row['catname'] if row['catname'] else 0
            sale_date = row['sale_date'] if row['sale_date'] else ""
            pur_date = row['pur_date'] if row['pur_date'] else ""
            if pur_date !="":

                purchase_date = datetime.strptime(pur_date, '%Y-%m-%d').strftime('%d-%m-%Y')
            else:
                purchase_date =""

            if sale_date != "":

                sales_date = datetime.strptime(sale_date, '%Y-%m-%d').strftime('%d-%m-%Y')
            else:
                sales_date = ""
            # sales_date = datetime.strptime(sale_date, '%Y-%m-%d').strftime('%d-%m-%Y')
            onhand = row['onhand'] if row['onhand'] else 0
            mrp = row['mrp'] if row['mrp'] else 0
            list_price= row['list_price'] if row['list_price'] else 0

            query2 = '''
                                               select aaal.product_id,
            max(aaal.price_unit) as costpt from 
            	account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                	left join product_product as pp on(pp.id=aaal.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)

                          where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid')
                           and aaa.date_invoice <=%s and aaal.product_id = %s and aaa.date_invoice in
                         (select max(aaa.date_invoice) from 
            account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                	left join product_product as pp on(pp.id=aaal.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                        where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice <=%s and aaal.product_id = %s 
                        and aaal.invoice_id in (select max(aaal.invoice_id) from account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                	left join product_product as pp on(pp.id=aaal.product_id)
                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                        where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') 
                        and aaa.date_invoice <=%s and aaal.product_id = %s group by  aaal.product_id) 
                        group by aaal.product_id )group by aaal.product_id
                                                            '''
            # query1 = '''
            # SELECT product_id,cost,id FROM product_price_history  WHERE product_id = %s and company_id = %s ORDER BY id DESC LIMIT 1
            # '''
            self.env.cr.execute(query2, (date_start, row['id'], date_start, row['id'], date_start, row['id']

                                         ))

            cost = 0
            for ans in self.env.cr.dictfetchall():
                cost = ans['costpt'] if ans['costpt'] else 0

            res = {
                'sl_no': sl,
                'id': row['id'] if row['id'] else '',
                'pname': row['pname'] if row['pname'] else '',
                'catname': row['catname'] if row['catname'] else '',
                'sale_date': sales_date,
                'pur_date': purchase_date,
                'onhand': row['onhand'] if row['onhand'] else 0,
                'mrp': row['mrp'] if row['mrp'] else 0,
                'list_price': row['list_price'] if row['list_price'] else 0,
                'cost': cost,

            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Brand'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 10)
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



        # vendor_name = self.env["res.partner"].browse(vendor_id).name

        company = self.env['res.company'].browse(data['form']['company_id']).name

        company_address = self.env['res.company'].browse(data['form']['company_id']).street


        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        font_size_888 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'align': 'center',})

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True})

        format11 = workbook.add_format(
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

        blue_mark2 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca', 'align': 'center'})

        blue_mark3 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 18, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca', 'align': 'center'})

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        # if brand_id:

        sheet.merge_range('A1:I1', company, blue_mark3)
        sheet.merge_range('A2:I2', company_address, blue_mark2)
        sheet.merge_range('A3:I3', " Negative Inventory Report ", blue_mark2)
        sheet.merge_range('A4:I4',  date_object_date_start.strftime(
            '%d-%m-%Y') , blue_mark2)
        # sheet.merge_range('A5:G5', "VENDOR NAME :- "+  vendor_name, blue_mark2)

        sheet.write('A7', "Sl No", blue_mark)
        sheet.write('B7', "Product Name", blue_mark)

        sheet.write('C7', "Category", blue_mark)
        sheet.write('D7', "MRP", blue_mark)
        sheet.write('E7', "HRP", blue_mark)
        sheet.write('F7', "On hand quantity", blue_mark)
        sheet.write('G7', "Last purchase date", blue_mark)
        sheet.write('H7', "Last Sale date", blue_mark)
        sheet.write('I7', "Cost", blue_mark)

        # config = self.env['product.brand'].browse(brand_only)
        # for pfg in config:

        linw_row = 7

        line_column = 0

        # if self.get_brand(data, pfg.id):



        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['pname'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['catname'], font_size_8)

            sheet.write(linw_row, line_column + 3, line['mrp'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['list_price'], font_size_8)
            # sheet.write(linw_row, line_column + 5, line['quantitypur'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['onhand'], font_size_8)
            sheet.write(linw_row, line_column + 6, line['pur_date'], font_size_888)
            sheet.write(linw_row, line_column + 7, line['sale_date'], font_size_888)
            sheet.write(linw_row, line_column + 8, line['cost'], font_size_8)

            linw_row = linw_row + 1
            line_column = 0






        # sheet.write(linw_row, 1, "TOTAL", format1)
        #
        # total_cell_range12 = xl_range(3, 3, linw_row - 1, 3)
        # total_cell_range11 = xl_range(3, 4, linw_row - 1, 4)
        # total_cell_range = xl_range(3, 5, linw_row - 1, 5)
        # total_cell_range_one = xl_range(3, 6, linw_row - 1, 6)
        # # total_cell_range_three = xl_range(3, 6, linw_row - 1, 6)
        #
        #
        # sheet.write_formula(linw_row, 3, '=SUM(' + total_cell_range12 + ')', format1)
        # sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range11 + ')', format1)
        # sheet.write_formula(linw_row, 5, '=SUM(' + total_cell_range + ')', format1)
        # sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_one + ')', format1)
        # sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_three + ')', format1)


Ainventory_pdf('report.negative_inventory_report.qlty_inventory_xls.xlsx', 'sale.order')
