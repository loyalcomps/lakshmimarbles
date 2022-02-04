from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from odoo import models,fields,api


class QltyCatpdf(models.AbstractModel):
    _name='report.qlty_sale_purchase_xls.salepurchase_report_pdf'

    def get_lines(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        sl = 0
        query = '''select purchase_amount, sale_amount,pos_sale_amount,
                        COALESCE( ssale_date,pos_date) AS  sale_date
                    from (
                        select purchase_amount, sale_amount, COALESCE( purchase_date, sale_date) AS ssale_date from 
                            (select SUM(a.amount_total) as purchase_amount,a.date_invoice as purchase_date from account_invoice as a
                                where a.type='in_invoice' and a.state in ('open','paid') and
                                a.company_id = %s and a.date_invoice BETWEEN %s and %s
                                GROUP BY a.date_invoice) aa
                        full join 

                        (select SUM(a.amount_total) as sale_amount,a.date_invoice as sale_date from account_invoice as a
                            where a.type='out_invoice' and a.state in ('open','paid') and
                            a.company_id = %s and a.date_invoice BETWEEN %s and %s
                            GROUP BY a.date_invoice) bb
                            on aa.purchase_date =bb.sale_date) aaa
                    full join

                        (select SUM(round(((pol.qty * pol.price_unit) - pol.discount),2) ) as pos_sale_amount,CAST(po.date_order AS DATE) as pos_date from pos_order_line as pol
                            left join pos_order as po
                            on po.id=pol.order_id
                            where  po.state in ('done','paid') and
                            po.company_id = %s and CAST(po.date_order AS DATE) BETWEEN %s and %s
                            GROUP BY CAST(po.date_order AS DATE)) cc
                            on aaa.ssale_date =cc.pos_date
                            order by sale_date




                        '''
        self.env.cr.execute(query, (company_id, date_start, date_end,
                                    company_id, date_start, date_end,
                                    company_id, date_start, date_end))
        for row in self.env.cr.dictfetchall():
            sl += 1
            sale_amount = row['sale_amount'] if row['sale_amount'] else 0
            pos_amount = row['pos_sale_amount'] if row['pos_sale_amount'] else 0

            dates = datetime.strptime(row['sale_date'], '%Y-%m-%d').date()

            res = {
                'sl_no': sl,
                'date': dates.strftime('%d-%m-%Y'),
                'sale': sale_amount + pos_amount,
                'purchase': row['purchase_amount'] if row['purchase_amount'] else 0

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

        get_lines = self.get_lines(data)

        date_object_startdate = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_enddate = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_startdate.strftime('%d-%m-%Y'),
            'date_end': date_object_enddate.strftime('%d-%m-%Y'),
            'data': data['form'],
            'get_lines': get_lines,
        }

        return self.env['report'].render('qlty_sale_purchase_xls.salepurchase_report_pdf', docargs)
