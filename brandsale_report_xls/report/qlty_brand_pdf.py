from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime

from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from odoo import models, fields, api


class Qltyvendorwisepdf(models.AbstractModel):
    _name ='report.brandsale_report_xls.qlty_brand_pdf'



    def get_brand(self, data):

        lines = []
        product = []
        average_cost = 0
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        brand_id = data['form']['brand_id']
        brand_only = data['form']['brand_only']
        category_id =data['form']['category_id']

        query = '''

        

  select ROW_NUMBER() OVER(ORDER BY dd.id ASC) AS slno,
                                               dd.id as id,dd.salepos_total as salepos_total ,dd.sale_total as sale_total,dd.purtotal as purtotal,



                                                dd.quantitypos as posquantity,
                                                dd.quantitysale as salequantity,
                                                dd.apsale_total as apsale_total,
                                                dd.apquantitysale as apsalequantity,
                                                (dd.sale_total-dd.apsale_total) as inv_saletotal, 
                                                (dd.quantitysale-dd.apquantitysale) as inv_qtytotal,

                                                ((dd.sale_total-dd.apsale_total)+dd.salepos_total) as tot_sale,
                                               
                                                
                                                
                                                dd.pquantitypur as pquantitypur,
                                                dd.name as dname,
                                                dd.productname as pname,
                                                 dd.pcname as pcname,
                                                 dd.freequantitypur as freequantitypur,
                                                 (dd.pquantitypur+dd.freequantitypur) as quantitypur

                                               from
                                               (

                                               (



                                select max(sh.product_id) as id,max(pb.name) as name,(pp.brand_id) as pb,max(pt.name) as productname
                                             ,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation,
                                             round(COALESCE(SUM(sm.price_unit * sm.product_qty),0)) as ion,max(pc.name) as pcname,max(pc.id)


                                            from stock_history  as sh
                                                left join product_product as pp on(pp.id=sh.product_id)
                                            left join product_template pt on (pt.id=pp.product_tmpl_id)
                                            left join product_brand as pb on (pb.id=pp.brand_id) 
                                            left join stock_move as sm on(sm.product_id = pp.id)
                                            left join product_category as pc on (pt.categ_id =pc.id)



                                           where  sh.company_id=%s and pc.id = %s group by 
                                                                   pp.brand_id

                                                                    ) a

                                                                   left join

                                                                                                   (
                                    select pp.brand_id as brand_id,max(aal.product_id) as product_id,sum(aal.price_subtotal_taxinc) as sale_total,sum(quantity) as quantitysale,
                                    round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as cccst

                                      from
                                    account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                                    left join product_product as pp on (pp.id = aal.product_id)
                                    left join product_template pt on (pt.id=pp.product_tmpl_id)
						            left join product_category as pc on (pt.categ_id =pc.id)
                                    
                                    where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                                    and  aa.company_id= %s and pc.id = %s
                                    
                                    

                                    group by pp.brand_id
                                                        ) h

                                                     

                                                                 on a.pb=h.brand_id
                                                                 
                                                                 full join

                                                
                                    (
                                    select pp.brand_id as brand_id,max(po.invoice_id),max(aal.product_id) ,sum(aal.price_subtotal_taxinc) as apsale_total,sum(quantity) as apquantitysale,
                                    round(SUM(aal.price_subtotal_taxinc/ nullif (aal.quantity,0)),2) as apcccst

                                      from
                                    account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
                                    left join pos_order as po on(po.invoice_id=aal.invoice_id)
                                    left join product_product as pp on (pp.id = aal.product_id)
                                    left join product_template pt on (pt.id=pp.product_tmpl_id)
						            left join product_category as pc on (pt.categ_id =pc.id)
                                    where aa.type ='out_invoice' and aa.state in  ('open', 'paid') and aa.date_invoice between %s and %s
                                    and  aa.company_id= %s and pc.id = %s
                                    and (aal.invoice_id=po.invoice_id)
                                    

                                    group by pp.brand_id
                                                        ) b

                                                         on a.pb=b.brand_id

                                                                 
                                                                 
                                                                 left join
                                               (

                                               select pp.brand_id as brand_id,max(aaal.product_id) as product_id,sum(aaal.price_subtotal_taxinc) as purtotal,sum(quantity) as pquantitypur ,sum(free_qty) as freequantitypur,
                                               round(SUM(aaal.price_subtotal_taxinc/ nullif (aaal.quantity,0)),2) as cscst 
                               	from
                                               account_invoice as aaa left join account_invoice_line as aaal on (aaa.id=aaal.invoice_id)
                                               left join product_product as pp on (pp.id = aaal.product_id)
                                               left join product_template pt on (pt.id=pp.product_tmpl_id)
						                        left join product_category as pc on (pt.categ_id =pc.id)
                                               where aaa.type ='in_invoice' and aaa.state in  ('open', 'paid') and aaa.date_invoice between %s and %s
                                               and  aaa.company_id= %s and pc.id = %s
                                                 group by pp.brand_id
                                                 ) c

                                               on c.brand_id=a.pb

                                                           left join

                               (
                                              select (pp.brand_id) as brand_id,max(pb.name),max(pol.product_id) as product_id ,sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,sum(pol.qty) as quantitypos
                                                from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                                                left join product_product as pp on(pp.id=pol.product_id)
                                               left join product_template pt on (pt.id=pp.product_tmpl_id)
                                               left join product_brand as pb on (pb.id=pp.brand_id)
						                        left join product_category as pc on (pt.categ_id =pc.id) 

                                                where
                                                po.state in  ('done', 'paid','invoiced')
                                               and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
                                               and pol.company_id= %s and pc.id = %s
                                               group by pp.brand_id)f on a.pb=f.brand_id)dd order by tot_sale



                                '''

        self.env.cr.execute(query, (company_id, (category_id),date_start, date_end, company_id,category_id,
                                    date_start, date_end, company_id,category_id,
                                    date_start, date_end, company_id,category_id
                                    , date_start, date_end, company_id,category_id

                                    ))

        for row in self.env.cr.dictfetchall():
            sale = 0
            possale = 0
            purtotal = 0
            # possale = row['salepos_total'] if row['salepos_total'] else 0
            # ptotal = row['purtotal'] if row['purtotal'] else 0
            # totalposqty = row['posquantity'] if row['posquantity'] else 0
            # quantitypur = row['quantitypur'] if row['quantitypur'] else 0
            # invoice_quantitytotal =row['invoice_quantitytotal'] if row['invoice_quantitytotal'] else 0
            # invoice_saletotal =row['invoice_saletotal'] if row['invoice_saletotal'] else 0
            # cscst=row['cscst'] if row['cscst'] else 0
            # totalsale = invoice_saletotal + possale


            aptotalsaleqty = row['apsalequantity'] if row['apsalequantity'] else 0
            apsale = row['apsale_total'] if row['apsale_total'] else 0

            # (dd.quantitysale - dd.apquantitysale) as inv_qtytotal,
            #
            # ((dd.sale_total - dd.apsale_total) + dd.salepos_total) as tot_sale,



            sale = row['sale_total'] if row['sale_total'] else 0
            # inv_saletotal = row['inv_saletotal'] if row['inv_saletotal'] else 0
            inv_qtytotal = row['inv_qtytotal'] if row['inv_qtytotal'] else 0

            possale = row['salepos_total'] if row['salepos_total'] else 0
            purtotal = row['purtotal'] if row['purtotal'] else 0

            inv_saletotal =sale-apsale
            totalsale = inv_saletotal + possale
            totalsaleqty = row['salequantity'] if row['salequantity'] else 0
            totalposqty = row['posquantity'] if row['posquantity'] else 0
            quantitypur = row['quantitypur'] if row['quantitypur'] else 0
            inv_qtytotal =totalsaleqty- aptotalsaleqty




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
                'sqty': inv_qtytotal + totalposqty,
                'quantitypur': quantitypur,



                'pcname': row['pcname'] if row['pcname'] else '',

                # 'totalsale':sale,


            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []



    @api.model
    def render_html(self, docids, data=None, config_id=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        brand_id = data['form']['brand_id']
        brand_only = data['form']['brand_only']
        category_id = data['form']['category_id']


        # get_lines = self.get_lines(data)
        get_brand = self.get_brand(data)
        # get_brand =self.get_brand(data)

        date_object_startdate = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_enddate = datetime.strptime(date_end, '%Y-%m-%d').date()
        category_name = self.env["product.category"].browse(category_id).name




        docargs = {

            'brand_only': brand_only,
            # 'config': config,
            # 'configures': configures,
            'data': data['form'],
            'doc_ids': self.ids,
            'date_start': date_object_startdate,
            'date_end': date_object_enddate,
            'data': data['form'],
            'brand_id': brand_id,
            'doc_ids': self.ids,
            'date_start': date_object_startdate.strftime('%d-%m-%Y'),
            'date_end': date_object_enddate.strftime('%d-%m-%Y'),

            'data': data['form'],
            # 'get_lines': get_lines if get_lines else 0,
            'get_brand':get_brand if get_brand else 0,
            'category_name':category_name

        }

        return self.env['report'].render('brandsale_report_xls.qlty_brand_pdf', docargs)