from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _


class Qltyproduct(ReportXlsx):


    def get_lines(self, data):

        lines = []



        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        product_id = data['form']['product_id']
        sl = 0
        query = ''' 
        
     

select 
ddd.id,
ddd.finalsaledate as fdate,
sum(ddd.posqty) as posqty,
sum(ddd.postotal) as postotal,
sum(ddd.saletotal) as saletotal,
sum(ddd.saleqty) as saleqty from 




(




  select

vv.ids as id,
COALESCE(vv.posdate ,vv.saledate )as finalsaledate,
vv.posqty as posqty,
vv.postotal as postotal,
vv.saletotal as saletotal,
vv.saleqty as saleqty

from 
(

                     

(


select 

dd.id as ids,
dd.posdate as posdate,
sum(dd.salepos_total) as postotal,
sum(dd.quantitypos) as posqty

from 
                       (

                       select   pp.id ,
                         sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,
                         sum(pol.qty) as quantitypos,
                       to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date as posdate
                        from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                        left join product_product as pp on(pp.id=pol.product_id)
                        left join product_template pt on (pt.id=pp.product_tmpl_id)
                        where
                        po.state in  ('done', 'paid','invoiced')
                      and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
                      and pol.company_id= %s and pp.id=%s
                        group by   pp.id,po.date_order 

                        ) as dd group by dd.id,dd.posdate)as hh 

                        full join
                        (
select 

ee.id,
ee.saledate as saledate,
sum(ee.sale_total) as saletotal,
sum(ee.quantitysale) as saleqty

from 
			(

			select  pp.id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale,
			to_char(date_trunc('day',aa.date_invoice),'YYYY-MM-DD')::date as saledate
			from account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
			left join product_product as pp on(pp.id=aal.product_id)
                        left join product_template pt on (pt.id=pp.product_tmpl_id)
			where 
			aa.type ='out_invoice' and aa.state in  ('open', 'paid')
			and to_char(date_trunc('day',aa.date_invoice),'YYYY-MM-DD')::date between %s and %s
                        and  aa.company_id= %s and aal.product_id=%s
                          group by   pp.id,aa.date_invoice

                           ) as ee group by ee.id,ee.saledate


                          ) as kk on(hh.posdate=kk.saledate))as vv 
                          order by finalsaledate ) as ddd group by ddd.id,ddd.finalsaledate 
                          order by ddd.finalsaledate 
        
        '''

        self.env.cr.execute(query, (
                                     date_start, date_end,company_id,product_id,
                                     date_start, date_end,company_id,product_id,
                                    ))
        for row in self.env.cr.dictfetchall():

            sl += 1

            salepos_total = row['postotal'] if row['postotal'] else 0
            sale_total = row['saletotal'] if row['saletotal'] else 0
            totalsaleqty = row['saleqty'] if row['saleqty'] else 0
            totalposqty = row['posqty'] if row['posqty'] else 0
            qty=totalsaleqty+totalposqty
            sale_pos=salepos_total+sale_total
            dates = datetime.strptime(row['fdate'], '%Y-%m-%d').date()

            res = {
                'sl_no': sl,
                'date': dates.strftime('%d-%m-%Y') if dates.strftime('%d-%m-%Y') else " ",
                'salepos_total':salepos_total,
                'sale_total':sale_total,

                'sale_pos':sale_pos if sale_pos else 0,

                'qty':qty if qty else 0,
                'totalposqty':totalposqty,
                'totalsaleqty':totalsaleqty


            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Date Wise Sale'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 14)
        sheet.set_column(1, 1, 25)
        sheet.set_column(2, 2, 17)
        sheet.set_column(3, 5, 17)
        sheet.set_default_row(20)

        # sheet.fit_to_pages(1, 0)
        # sheet.set_zoom(80)
        # sheet.set_column(0, 0, 8)
        # sheet.set_column(1, 1, 20)
        # sheet.set_column(2, 2, 25)
        # sheet.set_column(3, 3, 25)
        # sheet.set_column(4, 4, 20)
        # sheet.set_column(5, 5, 10)
        # sheet.set_column(6, 6, 20)
        # sheet.set_column(7, 7, 20)
        # sheet.set_column(8, 8, 20)
        # sheet.set_column(9, 9, 20)
        # sheet.set_column(10, 10, 20)
        # sheet.set_column(11, 11, 20)
        # sheet.set_column(12, 12, 20)
        # sheet.set_column(13, 13, 20)
        # sheet.set_column(14, 14, 20)
        # sheet.set_column(15, 15, 20)
        # sheet.set_column(16, 16, 20)
        # sheet.set_column(17, 17, 20)
        # sheet.set_column(18, 18, 20)
        # sheet.set_column(19, 19, 20)
        # sheet.set_column(20, 20, 20)

        date_start = data['form']['date_start']

        date_end = data['form']['date_end']

        product_id = data['form']['product_id']
        product=self.env["product.product"].browse(data['form']['product_id']).name

        company = self.env["res.company"].browse(data['form']['company_id']).name

        company_address= self.env["res.company"].browse(data['form']['company_id']).street


        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        font_size_88 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'align': 'center'})


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
             'color': 'ffffff', 'bg_color': '483D8B',})
        blue_mark1 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': 'ffffff', 'bg_color': '483D8B', 'align': 'center'})

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()

        sheet.merge_range('A1:D1', company, format2)
        sheet.merge_range('A2:D2', company_address, format2)
        sheet.merge_range('A3:D3', "Date Wise Sale Analysis ", format2)
        sheet.merge_range('A4:D4', date_object_date_start.strftime('%d-%m-%Y') + ' - ' + date_object_date_end.strftime('%d-%m-%Y'), format2)
        sheet.merge_range('A5:D5', " ", format2)


        sheet.write('A6', " ", blue_mark)

        sheet.write('B6', "Product : ", blue_mark)
        sheet.merge_range('C6:D6', product, blue_mark)

        # sheet.merge_range('A1:B1', "Category Wise Report ", format1)
        # sheet.write('C1', category_name, format1)
        # sheet.write('D1', "DATE :-", format1)
        # sheet.merge_range('E1:F1', date_start + ' - ' + date_end, format1)

        sheet.write('A8', "Sl No", blue_mark1)
        sheet.write('B8', "Date", blue_mark1)
        sheet.write('C8', "Quantity", blue_mark1)
        sheet.write('D8', "Total", blue_mark1)
        # sheet.write('E6', "Total", blue_mark)



        linw_row = 8

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_88)
            sheet.write(linw_row, line_column + 1, line['date'], font_size_88)
            sheet.write(linw_row, line_column + 2, line['qty'], font_size_8)
            sheet.write(linw_row, line_column + 3, line['sale_pos'], font_size_8)
            # sheet.write(linw_row, line_column + 4, (line['sale_total']*line['qty']), font_size_8)




            linw_row = linw_row + 1
            line_column = 0

        line_column = 0


        sheet.merge_range(linw_row, 0,linw_row, 1, "TOTAL", format1)

        total_cell_range11 = xl_range(8, 2, linw_row - 1, 2)
        total_cell_range = xl_range(8, 3, linw_row - 1, 3)

        sheet.write_formula(linw_row, 2, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 3, '=SUM(' + total_cell_range + ')', format1)


Qltyproduct('report.qlty_productsale_xls.qlty_productsale_xls.xlsx', 'sale.order')
