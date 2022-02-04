from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from odoo.tools.translate import _
from datetime import datetime


class Qltystockleadger(ReportXlsx):

    def get_lines(self, data):
        lines = []
        product=[]
        average_cost=0
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        product_ids = data['form']['product_ids']
        categ_ids = data['form']['categ_ids']
        company_id = data['form']['company_id']
        sl=0


        query = ''' select
                              dd.id as id,dd.pname as pname,
                              dd.categ as categ,
                              dd.salepos_total as salepos_total ,
                              dd.sale_total as sale_total,
                              dd.onhand as onhand,
                              dd.valuation as valuation,
                              dd.quantitypos as posquantity,dd.quantitysale as salequantity,dd.salecost as salecost,
                              dd.quantitypur as quantitypur
                              ,dd.pur_total as pur_total
                               from (
                              (
                                    select sh.product_id as id ,pt.name as pname, sum (sh.quantity) as onhand,
                                    pc.id as categ,
                                    round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                                    from stock_history as sh
                               left join product_product as pp on(pp.id=sh.product_id)
                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                               left join product_category pc on (pc.id=pt.categ_id)
                                where  sh.company_id = %s
                                  group by sh.product_id,pt.name
                                  , pc.id
                                   ) a
                                                              left join
                              (
                              select aal.product_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale
                               from
                              account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                           left join product_product as pp on(pp.id=aal.product_id)
                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                              where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                              and  aa.company_id= %s
                             group by aal.product_id
                             ) b
                                                            on a.id=b.product_id
                                                            left join
                              (
                              select aaal.product_id ,sum(aaal.price_subtotal) as pur_total,sum(quantity) as quantitypur from
                              account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                          left join product_product as pp on(pp.id=aaal.product_id)
                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                              where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between  %s and %s
                              and  aaa.company_id= %s
                          group by aaal.product_id
                          ) c
                              on a.id=c.product_id
                                              left join
                              (
                              select pol.product_id  ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                               from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                               left join product_product as pp on(pp.id=pol.product_id)
                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                               where
                               po.state in  ('done', 'paid','invoiced')
                              and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and %s
                               and pol.company_id= %s

                               group by pol.product_id
                                  ) d
                                                              on a.id=d.product_id
                                                              left join
                       (
                        select pt.id as product_id ,sum (sh.quantity) as onhands,
                                                              round(COALESCE(SUM(  sh.price_unit_on_quant * sh.quantity),0)) as salecost
                           from stock_history as sh
                               left join product_product as pp on(pp.id=sh.product_id)
                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                               left join product_category pc on (pc.id=pt.categ_id)
                                where  available_in_pos =True
                                and sh.quantity < 0
                                and to_char(date_trunc('day',sh.date),'YYYY-MM-DD')::date between  %s and %s and
                                sh.company_id = %s
                                  group by pt.id

                                  ) f
                                                              on a.id=f.product_id

                          left join
                      (
                      with pos as(
                      select
                      ddd.product_id ,
                      ddd.categ_id,
                      ddd.valuation,
                      ddd.totalquantitysale,
                      ddd.avg
                       from
                      (
                      (
                      select a.product_id as product_id,
                      a.categ_id,
                      a.quantity,
                      a.valuation
                       from (
                          select pc.name as psname,max(sh.product_categ_id) as categ_id,max(sh.product_id) as product_id,sum(sh.quantity) as quantity,
                          round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                              from stock_history sh left join product_template p on (p.id = sh.product_template_id)
                              left join product_category pc on (pc.id=sh.product_categ_id) where
                                available_in_pos = True  group by sh.product_id,pc.name,sh.product_categ_id order by max(sh.product_id)
                                ) a where  a.quantity <0
                      ) aa
                      left join
                      (
                      Select
                      COALESCE(product_id ,product_ids )as product_ids,

                      (COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) as totalsale,
                        (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) as totalquantitysale,
                      round((COALESCE  ((COALESCE( dd.salepos_total, '0' ) + COALESCE( dd.sale_total, '0' ) ) /   (  COALESCE( dd.quantitypos, '0' )+ COALESCE( dd.quantitysale, '0' )) )),0) as avg
                       from
                        (
                                (
                                select DISTINCT(aal.product_id),sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale from account_invoice aaa left join
                                 account_invoice_line aal  on   (aaa.id=aal.invoice_id)
                                   where aaa.type ='out_invoice' and aaa.state in  ('open', 'paid') group by aal.product_id order by   aal.product_id
                                   )  a
                       full join
                                  (
                                  select DISTINCT(pol.product_id ) product_ids ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                               from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                               left join product_product as pp on(pp.id=pol.product_id)
                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                               where
                               po.state in  ('done', 'paid','invoiced') group by pol.product_id order by  pol.product_id
                                ) b
                               on a.product_id =b.product_ids  ) dd where
                             dd.quantitypos !=0
                      ) bb on aa.product_id = bb.product_ids  ) ddd  )
                      select product_id,
                      totalquantitysale,
                       avg
                       from pos
                      ) g   on a.id=g.product_id
                              ) as dd 


                        '''

        if categ_ids and not product_ids:
            query = query + ''' where dd.categ in %s order by dd.pname '''

            self.env.cr.execute(query, (company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    tuple(categ_ids),
                                    ))
        elif not categ_ids and  product_ids:
            query = query + ''' where dd.id in %s order by dd.pname '''

            self.env.cr.execute(query, (company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    tuple(product_ids),
                                    ))

        elif categ_ids and  product_ids:
            query = query + ''' where dd.categ in %s and dd.id in %s order by dd.pname '''

            self.env.cr.execute(query, (company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    tuple(categ_ids),
                                    tuple(product_ids),
                                    ))
        else:

            self.env.cr.execute(query, (company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    date_start, date_end, company_id,
                                    ))

        for row in self.env.cr.dictfetchall():

            sl = sl + 1


            sale = 0
            possale = 0
            purtotal = 0
            sale = row['sale_total'] if row['sale_total'] else 0
            purtotalqty = row['sale_total'] if row['sale_total'] else 0
            possale = row['salepos_total'] if row['salepos_total'] else 0
            purtotal = row['pur_total'] if row['pur_total'] else 0
            onhand = row['onhand'] if row['onhand'] else 0
            onhandtotal = row['valuation'] if row['valuation'] else 0
            totalsale = sale + possale
            totalsaleqty = row['salequantity'] if row['salequantity'] else 0
            totalposqty = row['posquantity'] if row['posquantity'] else 0
            totalsaleqty = totalsaleqty + totalposqty
            quantitypur=row['quantitypur'] if row['quantitypur'] else 0

            res = {
                'sl_no': sl,
                'id': row['id'],
                'pname': row['pname'] if row['pname'] else '',
                'pur_total': round(purtotal, 0),
                'quantitypur': round(quantitypur, 0),
                'totalsaleqty': round(totalsaleqty, 0),
                'sale_total': round(totalsale, 0),
                'onhand': round(onhand, 0),
                'onhandtotal': round(onhandtotal, 0),

            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Category'))
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

        date_end = data['form']['date_end']

        company = self.env['res.company'].browse(data['form']['company_id']).name

        company_address = self.env['res.company'].browse(data['form']['company_id']).street


        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

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
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        sheet.merge_range('A1:H1', company, blue_mark3)
        sheet.merge_range('A2:H2', company_address, blue_mark2)
        sheet.merge_range('A3:H3', "Stock Leadger Report ", blue_mark2)
        sheet.merge_range('A4:H4','From ' + date_object_date_start.strftime('%d-%m-%Y') + ' - To ' + date_object_date_end.strftime('%d-%m-%Y'),blue_mark2)



        sheet.write('A7', "Sl No", blue_mark)
        sheet.write('B7', "Product", blue_mark)
        sheet.write('C7', "Purchase Qty", blue_mark)
        sheet.write('D7', "Purchase Amount", blue_mark)
        sheet.write('E7', "Sale Qty", blue_mark)
        sheet.write('F7', "Sale Amount", blue_mark)
        sheet.write('G7', "Current Inventory Qty", blue_mark)
        sheet.write('H7', "Current Inventory Value", blue_mark)
        # sheet.write('H7', "Profit", blue_mark)


        linw_row = 7

        line_column = 0


        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['pname'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['quantitypur'], font_size_8)
            sheet.write(linw_row, line_column + 3, line['pur_total'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['totalsaleqty'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['sale_total'], font_size_8)
            sheet.write(linw_row, line_column + 6, line['onhand'], font_size_8)
            sheet.write(linw_row, line_column + 7, line['onhandtotal'], font_size_8)

            linw_row = linw_row + 1
            line_column = 0

        line_column = 0


        sheet.write(linw_row, 1, "TOTAL", format1)

        total_cell_range12 = xl_range(3, 2, linw_row - 1, 2)
        total_cell_range11 = xl_range(3, 3, linw_row - 1, 3)
        total_cell_range = xl_range(3, 4, linw_row - 1, 4)
        total_cell_range_one = xl_range(3, 5, linw_row - 1, 5)
        total_cell_range_three = xl_range(3, 6, linw_row - 1, 6)
        total_cell_range_four = xl_range(3, 7, linw_row - 1, 7)

        sheet.write_formula(linw_row, 2, '=SUM(' + total_cell_range12 + ')', format1)
        sheet.write_formula(linw_row, 3, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range + ')', format1)
        sheet.write_formula(linw_row, 5, '=SUM(' + total_cell_range_one + ')', format1)
        sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_three + ')', format1)
        sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range_four + ')', format1)

Qltystockleadger('report.qlty_stockleadger_xls.qlty_stockleadger_xls.xlsx', 'sale.order')
