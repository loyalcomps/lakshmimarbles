from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from odoo import fields,api,models,_

from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from odoo import models,fields,api

class Qltyproductsalepdf(models.AbstractModel):
    _name='report.qlty_productsale_xls.productsale_report_pdf'

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
            date_start, date_end, company_id, product_id,
            date_start, date_end, company_id, product_id,
        ))
        for row in self.env.cr.dictfetchall():
            sl += 1

            salepos_total = row['postotal'] if row['postotal'] else 0
            sale_total = row['saletotal'] if row['saletotal'] else 0
            totalsaleqty = row['saleqty'] if row['saleqty'] else 0
            totalposqty = row['posqty'] if row['posqty'] else 0
            qty = totalsaleqty + totalposqty
            sale_pos = salepos_total + sale_total
            dates = datetime.strptime(row['fdate'], '%Y-%m-%d').date()

            res = {
                'sl_no': sl,
                'date': dates.strftime('%d-%m-%Y') if dates.strftime('%d-%m-%Y') else " ",
                'salepos_total': salepos_total,
                'sale_total': sale_total,

                'sale_pos': sale_pos if sale_pos else 0,

                'qty': qty if qty else 0,
                'totalposqty': totalposqty,
                'totalsaleqty': totalsaleqty

            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []


    @api.model
    def render_html(self, docids, data=None, ):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        product_id = data['form']['product_id']
        get_lines = self.get_lines(data)

        date_object_startdate = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_enddate = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'product_id':product_id,
            'doc_ids': self.ids,
            'date_start': date_object_startdate.strftime('%d-%m-%Y'),
            'date_end': date_object_enddate.strftime('%d-%m-%Y'),

            'data': data['form'],
            'get_lines': get_lines,
        }

        return self.env['report'].render('qlty_productsale_xls.productsale_report_pdf', docargs)
