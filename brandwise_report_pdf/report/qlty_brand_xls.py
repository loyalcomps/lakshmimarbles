from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime


class Brandrwise(ReportXlsx):

    def get_lines(self, data):
        lines = []
        product = []
        average_cost = 0
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        brand_id = data['form']['brand_id']
        brand_only = data['form']['brand_only']

        if brand_id:
            query1="""select ROW_NUMBER() OVER(ORDER BY dd.id ASC) AS slno,
                                           dd.id as id,dd.salepos_total as salepos_total ,dd.sale_total as sale_total,dd.purtotal as purtotal,
                                            dd.apsale_total as apsale_total,
                                            dd.apquantitysale as apsalequantity,
                                            (dd.sale_total-apsale_total) as invoice_saletotal,
                                            (dd.quantitysale-dd.apquantitysale) as invoice_quantitytotal,
                                            
                                            ((dd.sale_total-apsale_total)+dd.salepos_total) as ssale,
                                            

                                             dd.quantitypos as posquantity,
                                             dd.quantitysale as salequantity,
                                             dd.qtypur as qtypur,
                                              dd.freequantitypur as freequantitypur,
                                               (dd.qtypur+dd.freequantitypur) as quantitypur,
                                             dd.name as dname,
                                             dd.productname as pname,
                                             dd.pcname as pcname,
                                             dd.cscst as cscst


                                            from
                                            (

                                            (


                                            select max(sh.product_id) as id,max(pb.name) as name,max(pb.id) as pb,max(pt.name) as productname
                                          ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation,
                                          round(COALESCE(SUM(sm.price_unit * sm.product_qty),0)) as ion,max(pc.name) as pcname,max(pc.id)


                                         from stock_history  as sh
                                             left join product_product as pp on(pp.id=sh.product_id)
                                         left join product_template pt on (pt.id=pp.product_tmpl_id)
                                         left join product_brand as pb on (pb.id=pp.brand_id) 
                                         left join product_category as pc on (pt.categ_id =pc.id)
                                         left join stock_move as sm on(sm.product_id = pp.id)


                                        where  sh.company_id=%s and pc.id = %s group by 
                                                                pb.id


                                                         ) a

                                                  left join      
                                    (
                                    select po.invoice_id,aal.product_id ,sum(aal.price_subtotal_taxinc) as apsale_total,sum(quantity) as apquantitysale,
                                    round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as apcccst

                                      from
                                    account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                                    left join pos_order as po on(po.invoice_id=aal.invoice_id)
                                    where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                                    and  aa.company_id= %s 
                                    and (aal.invoice_id=po.invoice_id)
                                    

                                    group by aal.product_id,po.invoice_id
                                                        ) b

                                                      on a.id=b.product_id

                                                      left join



                                                      (
                                    select aal.product_id ,sum(aal.price_subtotal_taxinc) as sale_total,sum(quantity) as quantitysale,
                                    round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as cccst

                                      from
                                    account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                                    
                                    where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                                    and  aa.company_id= %s 
                                    
                                    

                                    group by aal.product_id
                                                        ) h

                                                      on a.id=h.product_id

                                                      left join
                                    (

                                    select aaal.product_id ,sum(aaal.price_subtotal_taxinc) as purtotal,sum(quantity) as qtypur ,sum(free_qty) as freequantitypur,
                                    round(SUM(aaal.price_subtotal_taxinc/ nullif (aaal.quantity,0)),2) as cscst 
                        from
                                    account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                                    where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
                                    and  aaa.company_id= %s
                                      group by aaal.product_id) c

                                    on c.product_id=a.id

                                                left join

                    (
                                    select pp.brand_id,max(pb.name),pol.product_id ,(sum(round(((pol.qty * pol.price_unit) - pol.discount),2))) as salepos_total,(sum(pol.qty)) as quantitypos
                                     from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                     left join product_product as pp on(pp.id=pol.product_id)
                                    left join product_template pt on (pt.id=pp.product_tmpl_id)
                                    left join product_brand as pb on (pb.id=pp.brand_id) 

                                     where
                                     po.state in  ('done', 'paid','invoiced')
                                    and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and %s
                                    and pol.company_id= %s
                                    group by pol.product_id,pp.brand_id)f on a.id=f.product_id)dd order by ssale
"""
            query = '''

                                select ROW_NUMBER() OVER(ORDER BY dd.id ASC) AS slno,
                                               dd.id as id,dd.salepos_total as salepos_total ,dd.sale_total as sale_total,dd.purtotal as purtotal,

                                                dd.quantitypos as posquantity,
                                                dd.quantitysale as salequantity,
                                                dd.quantitypur as quantitypur,
                                                dd.name as dname,
                                                dd.productname as pname

                                               from
                                               (

                                               (



                                select sh.product_id as id,max(pb.name) as name,pb.id as pb,max(pt.name) as productname
                                             ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation,
                                             round(COALESCE(SUM(sm.price_unit * sm.product_qty),0)) as ion


                                            from stock_history  as sh
                                                left join product_product as pp on(pp.id=sh.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)
                                            left join product_brand as pb on (pb.id=pp.brand_id) 
                                            left join stock_move as sm on(sm.product_id = pp.id)


                                           where  sh.company_id=%s and pb.id in %s group by 
                                                                   sh.product_id,pb.id

                                                                    ) a

                                                                   left join

                                               (
                                               select aal.product_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale,
                                               round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as cccst

                                                 from
                                               account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                                               where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                                               and  aa.company_id= %s group by aal.product_id

                                                                   ) b

                                                                 on a.id=b.product_id

                                                                 left join
                                               (

                                               select aaal.product_id ,sum(aaal.price_subtotal) as purtotal,sum(quantity) as quantitypur ,
                                               round(SUM(aaal.price_subtotal_taxinc/ nullif (aaal.quantity,0)),2) as cscst 
                               	from
                                               account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                                               where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
                                               and  aaa.company_id= %s
                                                 group by aaal.product_id) c

                                               on c.product_id=a.id

                                                           left join

                               (
                                               select pp.brand_id,max(pb.name),pol.product_id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                                from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                                left join product_product as pp on(pp.id=pol.product_id)
                                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                                               left join product_brand as pb on (pb.id=pp.brand_id) 

                                                where
                                                po.state in  ('done', 'paid','invoiced')
                                               and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and %s
                                               and pol.company_id= %s
                                               group by pol.product_id,pp.brand_id)f on a.id=f.product_id)dd 

                                                                      '''
            self.env.cr.execute(query, (company_id, tuple(brand_id),
                                        date_start, date_end, company_id, date_start, date_end, company_id,
                                        date_start, date_end, company_id,
                                        ))

            for row in self.env.cr.dictfetchall():
                sale = 0
                possale = 0
                purtotal = 0
                sale = row['sale_total'] if row['sale_total'] else 0
                possale = row['salepos_total'] if row['salepos_total'] else 0
                purtotal = row['purtotal'] if row['purtotal'] else 0
                totalsale = sale + possale
                totalsaleqty = row['salequantity'] if row['salequantity'] else 0
                totalposqty = row['posquantity'] if row['posquantity'] else 0
                quantitypur = row['quantitypur'] if row['quantitypur'] else 0

                res = {
                    'sl_no': row['slno'],
                    'id': row['id'],
                    'pname': row['pname'] if row['pname'] else '',
                    'bname': row['dname'] if row['dname'] else '',
                    'sale': sale,
                    'possale': possale,
                    'purtotal': purtotal,
                    'totalsale': totalsale,
                    'totalsaleqty': totalsaleqty,
                    'totalposqty ': totalposqty,
                    'sqty': totalsaleqty + totalposqty,
                    'quantitypur': quantitypur
                }

                lines.append(res)

            if lines:
                return lines
            else:
                return []

    def get_brand(self, data):

        lines = []
        product = []
        average_cost = 0
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        brand_id = data['form']['brand_id']
        brand_only = data['form']['brand_only']

        query = '''

           select ROW_NUMBER() OVER(ORDER BY dd.id ASC) AS slno,
                                       dd.id as id,dd.salepos_total as salepos_total ,dd.sale_total as sale_total,dd.purtotal as purtotal,

                                        dd.quantitypos as posquantity,
                                        dd.quantitysale as salequantity,
                                        dd.quantitypur as quantitypur,
                                        dd.name as dname,
                                        dd.productname as pname

                                       from
                                       (

                                       (



                        select sh.product_id as id,max(pb.name) as name,pb.id as pb,max(pt.name) as productname
                                     ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation,
                                     round(COALESCE(SUM(sm.price_unit * sm.product_qty),0)) as ion


                                    from stock_history  as sh
                                        left join product_product as pp on(pp.id=sh.product_id)
                                    left join product_template pt on (pt.id=pp.product_tmpl_id)
                                    left join product_brand as pb on (pb.id=pp.brand_id) 
                                    left join stock_move as sm on(sm.product_id = pp.id)


                                   where  sh.company_id=%s group by 
                                                           sh.product_id,pb.id

                                                            ) a

                                                           left join

                                       (
                                       select aal.product_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale,
                                       round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as cccst

                                         from
                                       account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                                       where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                                       and  aa.company_id= %s group by aal.product_id

                                                           ) b

                                                         on a.id=b.product_id

                                                         left join
                                       (

                                       select aaal.product_id ,sum(aaal.price_subtotal) as purtotal,sum(quantity) as quantitypur ,
                                       round(SUM(aaal.price_subtotal_taxinc/ nullif (aaal.quantity,0)),2) as cscst 
                           from
                                       account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                                       where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
                                       and  aaa.company_id= %s
                                         group by aaal.product_id) c

                                       on c.product_id=a.id

                                                   left join

                       (
                                       select pp.brand_id,max(pb.name),pol.product_id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                        from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                        left join product_product as pp on(pp.id=pol.product_id)
                                       left join product_template pt on (pt.id=pp.product_tmpl_id)
                                       left join product_brand as pb on (pb.id=pp.brand_id) 

                                        where
                                        po.state in  ('done', 'paid','invoiced')
                                       and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and %s
                                       and pol.company_id= %s
                                       group by pol.product_id,pp.brand_id)f on a.id=f.product_id)dd 


                                   '''

        self.env.cr.execute(query, (company_id, date_start, date_end, company_id, date_start, date_end, company_id
                                    , date_start, date_end, company_id
                                    ))

        for row in self.env.cr.dictfetchall():
            sale = 0
            possale = 0
            purtotal = 0
            sale = row['sale_total'] if row['sale_total'] else 0
            possale = row['salepos_total'] if row['salepos_total'] else 0
            purtotal = row['purtotal'] if row['purtotal'] else 0
            totalsale = sale + possale
            totalsaleqty = row['salequantity'] if row['salequantity'] else 0
            totalposqty = row['posquantity'] if row['posquantity'] else 0
            quantitypur = row['quantitypur'] if row['quantitypur'] else 0

            res = {
                'sl_no': row['slno'],
                'id': row['id'],
                'pname': row['pname'] if row['pname'] else '',
                'bname': row['dname'] if row['dname'] else '',
                'sale': sale,
                'possale': possale,
                'purtotal': purtotal,
                'totalsale': totalsale,
                'totalsaleqty': totalsaleqty,
                'totalposqty ': totalposqty,
                'sqty': totalsaleqty + totalposqty,
                'quantitypur': quantitypur
            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []
    # def get_brand(self, data, config_id):
    #     lines = []
    #     product = []
    #     average_cost = 0
    #     date_start = data['form']['date_start']
    #     date_end = data['form']['date_end']
    #     company_id = data['form']['company_id']
    #     brand_id = data['form']['brand_id']
    #     brand_only = data['form']['brand_only']
    #
    #     sl = 0
    #
    #     if brand_only:
    #         query = '''
    #
    #          select ROW_NUMBER() OVER(ORDER BY dd.id ASC) AS slno,
    #                         dd.id as id,dd.salepos_total as salepos_total ,dd.sale_total as sale_total,dd.purtotal as purtotal,
    #
    #                          dd.quantitypos as posquantity,
    #                          dd.quantitysale as salequantity,
    #                          dd.quantitypur as quantitypur,
    #                          dd.name as dname,
    #                          dd.productname as pname
    #
    #                         from
    #                         (
    #
    #                         (
    #
    #
    #
    #          select sh.product_id as id,max(pb.name) as name,pb.id as pb,max(pt.name) as productname
    #                       ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation,
    #                       round(COALESCE(SUM(sm.price_unit * sm.product_qty),0)) as ion
    #
    #
    #                      from stock_history  as sh
    #                          left join product_product as pp on(pp.id=sh.product_id)
    #                      left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                      left join product_brand as pb on (pb.id=pp.brand_id)
    #                      left join stock_move as sm on(sm.product_id = pp.id)
    #
    #
    #                     where  sh.company_id=%s and pb.id = %s group by
    #                                             sh.product_id,pb.id
    #
    #                                              ) a
    #
    #                                             left join
    #
    #                         (
    #                         select aal.product_id ,sum(aal.price_subtotal) as sale_total,sum(quantity) as quantitysale,
    #                         round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as cccst
    #
    #                           from
    #                         account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
    #                         where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
    #                         and  aa.company_id= %s group by aal.product_id
    #
    #                                             ) b
    #
    #                                           on a.id=b.product_id
    #
    #                                           left join
    #                         (
    #
    #                         select aaal.product_id ,sum(aaal.price_subtotal) as purtotal,sum(quantity) as quantitypur ,
    #                         round(SUM(aaal.price_subtotal_taxinc/ nullif (aaal.quantity,0)),2) as cscst
    #         	from
    #                         account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
    #                         where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
    #                         and  aaa.company_id= %s
    #                           group by aaal.product_id) c
    #
    #                         on c.product_id=a.id
    #
    #                                     left join
    #
    #         (
    #                         select pp.brand_id,max(pb.name),pol.product_id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
    #                          from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
    #                          left join product_product as pp on(pp.id=pol.product_id)
    #                         left join product_template pt on (pt.id=pp.product_tmpl_id)
    #                         left join product_brand as pb on (pb.id=pp.brand_id)
    #
    #                          where
    #                          po.state in  ('done', 'paid','invoiced')
    #                         and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between  %s and %s
    #                         and pol.company_id= %s
    #                         group by pol.product_id,pp.brand_id)f on a.id=f.product_id)dd
    #
    #                                                '''
    #         self.env.cr.execute(query, (
    #             date_start, date_end, company_id, (config_id), date_start, date_end, company_id,
    #             date_start, date_end, company_id,
    #         ))
    #         for row in self.env.cr.dictfetchall():
    #             sale = 0
    #             possale = 0
    #             purtotal = 0
    #             sale = row['sale_total'] if row['sale_total'] else 0
    #             possale = row['salepos_total'] if row['salepos_total'] else 0
    #             purtotal = row['purtotal'] if row['purtotal'] else 0
    #             totalsale = sale + possale
    #             totalsaleqty = row['salequantity'] if row['salequantity'] else 0
    #             totalposqty = row['posquantity'] if row['posquantity'] else 0
    #             quantitypur = row['quantitypur'] if row['quantitypur'] else 0
    #
    #             res = {
    #                 'sl_no': row['slno'],
    #                 'id': row['id'],
    #                 'bname': row['dname'] if row['dname'] else '',
    #                 'pname': row['pname'] if row['pname'] else '',
    #                 'sale': sale,
    #                 'possale': possale,
    #                 'purtotal': purtotal,
    #                 'totalsale': totalsale,
    #                 'totalsaleqty': totalsaleqty,
    #                 'totalposqty ': totalposqty,
    #                 'sqty': totalsaleqty + totalposqty,
    #                 'quantitypur': quantitypur
    #             }
    #
    #             lines.append(res)
    #
    #         if lines:
    #             return lines
    #         else:
    #             return []



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

        date_end = data['form']['date_end']
        brand_id = data['form']['brand_id']
        brand_only = data['form']['brand_only']

        # vendor_name = self.env["res.partner"].browse(vendor_id).name

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

        # if brand_id:

        sheet.merge_range('A1:G1', company, blue_mark3)
        sheet.merge_range('A2:G2', company_address, blue_mark2)
        sheet.merge_range('A3:G3', "Brand Wise Report ", blue_mark2)
        sheet.merge_range('A4:G4', 'From ' + date_object_date_start.strftime(
            '%d-%m-%Y') + ' - To ' + date_object_date_end.strftime('%d-%m-%Y'), blue_mark2)
        # sheet.merge_range('A5:G5', "VENDOR NAME :- "+  vendor_name, blue_mark2)

        sheet.write('A7', "Sl No", blue_mark)
        sheet.write('B7', "Product Name", blue_mark)

        sheet.write('C7', "Brand", blue_mark)
        sheet.write('D7', "Sale Quantity", blue_mark)
        sheet.write('E7', "Sale Amount", blue_mark)
        sheet.write('F7', "Purchase Quantity", blue_mark)
        sheet.write('G7', "Purchase Amount", blue_mark)
        # sheet.write('G7', "Profit", blue_mark)

        # config = self.env['product.brand'].browse(brand_only)
        # for pfg in config:

        linw_row = 7

        line_column = 0

        # if self.get_brand(data, pfg.id):



        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['pname'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['bname'], font_size_8)

            sheet.write(linw_row, line_column + 3, line['sqty'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['totalsale'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['quantitypur'], font_size_8)
            sheet.write(linw_row, line_column + 6, line['purtotal'], font_size_8)
            # sheet.write(linw_row, line_column + 6, line['profit'], font_size_8)

            linw_row = linw_row + 1
            line_column = 0





        for line in self.get_brand(data):
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column + 1, line['pname'], font_size_8)
            sheet.write(linw_row, line_column + 2, line['bname'], font_size_8)

            sheet.write(linw_row, line_column + 3, line['sqty'], font_size_8)
            sheet.write(linw_row, line_column + 4, line['totalsale'], font_size_8)
            sheet.write(linw_row, line_column + 5, line['quantitypur'], font_size_8)
            sheet.write(linw_row, line_column + 6, line['purtotal'], font_size_8)
            # sheet.write(linw_row, line_column + 6, line['profit'], font_size_8)

            linw_row = linw_row + 1
            line_column = 0

        line_column = 0

        sheet.write(linw_row, 1, "TOTAL", format1)

        total_cell_range12 = xl_range(3, 3, linw_row - 1, 3)
        total_cell_range11 = xl_range(3, 4, linw_row - 1, 4)
        total_cell_range = xl_range(3, 5, linw_row - 1, 5)
        total_cell_range_one = xl_range(3, 6, linw_row - 1, 6)
        # total_cell_range_three = xl_range(3, 6, linw_row - 1, 6)


        sheet.write_formula(linw_row, 3, '=SUM(' + total_cell_range12 + ')', format1)
        sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 5, '=SUM(' + total_cell_range + ')', format1)
        sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_one + ')', format1)
        # sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_three + ')', format1)


Brandrwise('report.brandsale_report_xls.qlty_brand_xls.xlsx', 'sale.order')
