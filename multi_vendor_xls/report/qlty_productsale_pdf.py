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

class Multyproductsalepdf(models.AbstractModel):
    _name='report.multi_vendor_xls.productsale_report_pdf'

    def get_lines(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        product_id = data['form']['product_id']
        sl = 0
        query = ''' 

    select 

    ee.id,
    ee.ppname as ppname,
    ee.purchasedate as purchasedate,
    sum(ee.purchase_total) as purchasetotal,
    sum(ee.quantitypurchase) as purchaseqty

    from 
    			(

    			select  pp.id ,sum(aal.price_subtotal_taxinc) as purchase_total,sum(quantity) as quantitypurchase,

    			to_char(date_trunc('day',aa.date_invoice),'YYYY-MM-DD')::date as purchasedate,p.name as ppname
    			from account_invoice as aa left join account_invoice_line as aal on (aa.id=aal.invoice_id)
    			left join product_product as pp on(pp.id=aal.product_id)
                            left join product_template pt on (pt.id=pp.product_tmpl_id)
                            left join res_partner as p on (p.id=aa.partner_id)

    			where 
    			aa.type ='in_invoice' and aa.state in  ('open', 'paid')
    			and to_char(date_trunc('day',aa.date_invoice),'YYYY-MM-DD')::date between %s and %s
                            and  aa.company_id= %s and aal.product_id=%s
                              group by   pp.id,aa.date_invoice,p.name

                               ) as ee group by ee.id,ee.purchasedate,ee.ppname

            '''

        self.env.cr.execute(query, (
            date_start, date_end, company_id, product_id,
        ))
        for row in self.env.cr.dictfetchall():
            sl += 1

            ppname = row['ppname'] if row['ppname'] else " "
            purchasedate = row['purchasedate'] if row['purchasedate'] else " "
            purchasetotal = row['purchasetotal'] if row['purchasetotal'] else 0
            purchaseqty = row['purchaseqty'] if row['purchaseqty'] else 0


            res = {
                'sl_no': sl,
                'ppname': ppname,
                'purchasedate': purchasedate,
                'purchasetotal': purchasetotal,
                'purchaseqty': purchaseqty

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

        return self.env['report'].render('multi_vendor_xls.productsale_report_pdf', docargs)
