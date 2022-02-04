from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from odoo.tools.translate import _
from odoo import models, fields, api



class qltyinvoicepdf(models.AbstractModel):

    _name = 'report.qlty_invoice_xls.invoice_report_pdf'

    def get_partnersum(self, data):
        lines = []
        res = {}

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_id = data['form']['branch_id']
        type = data['form']['type']

        query = '''select max(i.date_invoice) as date,max(p.name) as partner,sum(i.amount_total) as total
    from account_invoice i left join res_partner p on (p.id = i.partner_id) where i.type= %s and i.date_invoice between %s and %s and i.company_id = %s and i.state in ('paid','open') group by p.name order by p.name  '''
        self.env.cr.execute(query, (type, date_start, date_end, branch_id))

        # lines = self.env.cr.dictfetchall()

        for row in self.env.cr.dictfetchall():
            res = {
                'date_invoice': row['date'],
                'partner': row['partner'],
                'amount_total': row['total'],
            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_lines(self, data):
        lines = []
        res = {}

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_id = data['form']['branch_id']
        type = data['form']['type']

        query = '''select i.date_invoice,i.number,p.name,i.reference,i.amount_tax,i.amount_untaxed,i.amount_discount,i.amount_total
from account_invoice i left join res_partner p on (p.id = i.partner_id) where i.type= %s and i.date_invoice between %s and %s and i.company_id = %s and i.state in ('paid','open') order by date_invoice
            '''
        self.env.cr.execute(query, (type, date_start, date_end, branch_id))

        # lines = self.env.cr.dictfetchall()

        for row in self.env.cr.dictfetchall():
            res = {
                'date_invoice': row['date_invoice'],
                'number': row['number'],
                'name': row['name'],
                'reference': row['reference'],
                'amount_tax': row['amount_tax'],
                'amount_untaxed': row['amount_untaxed'],
                'amount_total': row['amount_total'],
                'amount_discount': row['amount_discount'],
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
        consol =data['form']['consolidated']
        get_partnersum = self.get_partnersum(data)
        get_lines = self.get_lines(data)


        date_object_startdate = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_enddate = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_startdate.strftime('%d-%m-%Y'),
            'date_end': date_object_enddate.strftime('%d-%m-%Y'),
            'consol':consol,
            'data': data['form'],
            'get_partnersum': get_partnersum,
            'get_lines':get_lines,
        }

        return self.env['report'].render('qlty_invoice_xls.invoice_report_pdf', docargs)



