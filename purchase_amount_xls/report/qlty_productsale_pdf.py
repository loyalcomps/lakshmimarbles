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

class Purchaseproductsalepdf(models.AbstractModel):
    _name='report.purchase_amount_xls.productsale_report_pdf'

    def get_lines(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        partner_id = data['form']['partner_id']
        sl = 0
        query = ''' 

   select 

dd.id as ids,
dd.poname as poname,
dd.prname as prname,


dd.posdate as posdate,
sum(dd.salepos_total) as postotal,
sum(dd.quantitypos) as posqty

from 
                       (

                       select   pp.id ,
                         sum(round(((pol.qty * pol.price_unit) - pol.discount),2)) as salepos_total,
                         sum(pol.qty) as quantitypos,
                       to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date as posdate,pt.name as prname,po.partner_id as poname
                        from pos_order as po left join pos_order_line as pol on (po.id=pol.order_id)
                        left join product_product as pp on(pp.id=pol.product_id)
                        left join product_template pt on (pt.id=pp.product_tmpl_id)
                        left join res_partner as p on (p.id=po.partner_id)
                        where
                        po.state in  ('done', 'paid','invoiced')
                      and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
                      and pol.company_id= %s and po.partner_id=%s
                        group by   pp.id,po.date_order,po.partner_id,pt.name

                        ) as dd group by dd.id,dd.posdate,dd.prname,dd.poname
            '''

        self.env.cr.execute(query, (
            date_start, date_end, company_id, partner_id,
        ))
        for row in self.env.cr.dictfetchall():
            sl += 1

            date = datetime.strptime(row['posdate'], '%Y-%m-%d').date()

            ppname = row['poname'] if row['poname'] else " "
            prname = row['prname'] if row['prname'] else " "

            # purchasedate = row['posdate'] if row['posdate'] else " "
            purchasetotal = row['postotal'] if row['postotal'] else 0
            purchaseqty = row['posqty'] if row['posqty'] else 0
            # productname = row['poname'] if row['poname'] else 0


            res = {
                'sl_no': sl,
                'ppname': ppname,
                'prname':prname,
                'purchasedate': date.strftime('%d-%m-%Y'),
                'purchasetotal': purchasetotal,
                'purchaseqty': purchaseqty,
                # 'productname':productname

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
        partner_id = data['form']['partner_id']
        get_lines = self.get_lines(data)

        partner = self.env["res.partner"].browse(data['form']['partner_id']).name

        phone = self.env["res.partner"].browse(data['form']['partner_id']).phone

        date_object_startdate = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_enddate = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'partner_id':partner_id,
            'doc_ids': self.ids,
            'date_start': date_object_startdate.strftime('%d-%m-%Y'),
            'date_end': date_object_enddate.strftime('%d-%m-%Y'),
            'partner':partner,
            'phone':phone,

            'data': data['form'],
            'get_lines': get_lines,
        }

        return self.env['report'].render('purchase_amount_xls.productsale_report_pdf', docargs)
