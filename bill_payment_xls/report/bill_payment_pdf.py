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

class Vendorbillpdf(models.AbstractModel):
    _name='report.bill_payment_xls.payment_report_pdf'

    def get_lines(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        vendor_id = data['form']['vendor_id']
        sl = 0
        query = ''' 

                    select COALESCE(dd.p_date) AS  pdate,
                               dd.amount as amount,dd.number as number,dd.reference as reference,dd.breference as breference,dd.pname as pname,dd.jname as ajname
                                from (
                                select abs.amount as amount,abs.check_number as number,abs.cheque_reference as reference,abs.bank_reference as breference,
                                COALESCE(abs.payment_date) AS  p_date,
                                abs.payment_type ptype,po.name as pname,aj.name as jname,
                                CAST(abs.payment_date AS DATE) as start_at from
                                       account_payment as abs
                                        left join account_payment_method as po on po.id=abs.payment_method_id
                                        left join account_journal as aj  on aj.id=abs.journal_id
                                        where  po.payment_type in ('outbound','inbound') and 
            				abs.company_id = %s and abs.partner_id=%s
            				and CAST(abs.payment_date AS DATE) between %s and %s

                                        GROUP BY CAST(abs.payment_date AS DATE),abs.amount,abs.check_number,abs.cheque_reference,
                                        po.name,aj.name,
                                        abs.bank_reference,abs.payment_type
                                        ) as dd order by dd.p_date

        '''

        self.env.cr.execute(query, (
            company_id, vendor_id, date_start, date_end,
        ))
        for row in self.env.cr.dictfetchall():
            sl += 1

            # date = datetime.strptime(row['pdate'], '%Y-%m-%d').date()

            res = {
                'date':row['pdate'] if row['pdate'] else " ",
                'sl_no': sl,
                'amount': row['amount'] if row['amount'] else " ",
                'reference': row['reference'] if row['reference'] else " ",
                'breference': row['breference'] if row['breference'] else " ",
                'pname': row['pname'] if row['pname'] else " ",
                'ajname': row['ajname'] if row['ajname'] else " ",
                'number': row['number'] if row['number'] else " ",

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
        vendor_id = data['form']['vendor_id']
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

        return self.env['report'].render('bill_payment_xls.payment_report_pdf', docargs)
