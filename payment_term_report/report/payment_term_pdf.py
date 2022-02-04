from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime
from odoo import models,fields,api,_


class qltybankbookpdf(models.AbstractModel):
    _name = 'report.payment_term_report.payment_term_pdf'

    def get_lines(self, data, vendor_id):

        lines = []
        res = {}
        result = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']

        name = ''
        phone = 0

        query = '''
            SELECT date_due,date_invoice,number,rp.name,rp.phone,rp.mobile,amount_total,(amount_total-residual) as paid,residual FROM account_invoice as ai
             left join res_partner as rp on rp.id = ai.partner_id
             where ai.type ='in_invoice'
             
             AND partner_id = %s and date_due BETWEEN %s and %s AND ai.company_id = %s AND ai.state ='open'
                      
            ORDER BY  date_due ASC
        '''
        self.env.cr.execute(query, (vendor_id,date_start,date_end, company_id,))
        for row in self.env.cr.dictfetchall():
            phone = row['mobile'] if row['mobile'] else row['phone']
            name = row['name']
            res = {

                'due_date': row['date_due'],
                'number': row['number'],
                'invoice_date': row['date_invoice'],
                'total_amount': row['amount_total'],
                'paid': row['paid'],
                'balance': row['residual'],

            }
            lines.append(res)
        result = {
            'partner_id':lines,
            'name':name,
            'mobile':phone if phone else '',

        }
        if lines:
            return result
        else:
            return []

    def get_payable_receivable(self, data):

        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']


        query = '''
            SELECT date_due,date_invoice,number,rp.name,rp.phone,rp.mobile,amount_total,(amount_total-residual) as paid,residual FROM account_invoice as ai
            left join res_partner as rp on rp.id = ai.partner_id where ai.type ='in_invoice' AND ai.state ='open'
             AND  date_due BETWEEN %s and %s AND ai.company_id = %s 
                      
            ORDER BY  date_due ASC
        '''
        self.env.cr.execute(query, (date_start,date_end, company_id))
        for row in self.env.cr.dictfetchall():
            phone = row['mobile'] if row['mobile'] else row['phone']
            res = {

                'name':row['name'],
                'phone': phone if phone else '',
                'due_date': row['date_due'],
                'number': row['number'],
                'invoice_date': row['date_invoice'],
                'total_amount': row['amount_total'],
                'paid': row['paid'],
                'balance': row['residual'],

            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []


    @api.model
    def render_html(self, docids, data=None):

        payrec_result = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        vendor_ids = data['form']['vendor_ids']
        total_payable_receivable = 0
        if vendor_ids:
            partners = self.env['res.partner'].browse(vendor_ids)
            for partner in partners:
                if self.get_lines(data, partner.id):

                    payrec_result.append(self.get_lines(data, partner.id))
        else:
            total_payable_receivable = self.get_payable_receivable(data)

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'doc_ids': self.ids,
            'date_start':date_object_date_start.strftime('%d-%m-%Y'),
            'date_end':date_object_date_end.strftime('%d-%m-%Y'),
            'total_payable_receivable':total_payable_receivable,
            'vendor_ids':vendor_ids,
            'payable_receivable':payrec_result,


        }

        return self.env['report'].render('payment_term_report.payment_term_pdf', docargs)



