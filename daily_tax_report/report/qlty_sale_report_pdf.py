# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportCategory(models.AbstractModel):

    _name = 'report.daily_tax_report.daily_report_pdf'

    def get_cash(self, data):

        lines = []
        invoice_id = []
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        stock_location = data['form']['stock_location']

        cr = 0



        query21 = '''
Select
                ROW_NUMBER() OVER(ORDER BY dd.date_invoice ASC) AS sl_no,
                dd.date_invoice as date_invoice,
                sum(dd.taxable) as total_taxable,
                sum(dd.tax_amount) as total_tax,
                sum(dd.total_am) as total,    
       
             COALESCE(sum(CASE WHEN dd.tax=0 or dd.tax is null THEN dd.tax_amount ELSE 0 END ),0)  as tax0,
            COALESCE(sum(CASE WHEN dd.tax=1 THEN dd.tax_amount ELSE 0 END ),0)  as tax1,
	        COALESCE(sum(CASE dd.tax WHEN 5 THEN dd.tax_amount ELSE 0 END ),0)  as tax5,
            COALESCE(sum(CASE  WHEN dd.tax = 12 THEN dd.tax_amount ELSE 0 END ),0)  as tax12,
            COALESCE(sum(CASE dd.tax WHEN 18 THEN dd.tax_amount ELSE 0 END ),0)  as tax18,
            COALESCE(sum(CASE dd.tax WHEN 28 THEN dd.tax_amount ELSE 0 END ),0)  as tax28,
            COALESCE(sum(CASE dd.tax WHEN 40 THEN dd.tax_amount ELSE 0 END ),0)  as cesstax,

            COALESCE(sum(CASE WHEN dd.tax=0 or dd.tax is null THEN dd.taxable ELSE 0 END ),0)  as taxable0,
            COALESCE(sum(CASE WHEN dd.tax=1 THEN dd.taxable ELSE 0 END ),0)  as taxable1,
	        COALESCE(sum(CASE dd.tax WHEN 5 THEN dd.taxable ELSE 0 END ),0)  as taxable5,
            COALESCE(sum(CASE  WHEN dd.tax = 12 THEN dd.taxable ELSE 0 END ),0)  as taxable12,
            COALESCE(sum(CASE dd.tax WHEN 18 THEN dd.taxable ELSE 0 END ),0)  as taxable18,
            COALESCE(sum(CASE dd.tax WHEN 28 THEN dd.taxable ELSE 0 END ),0)  as taxable28,
            COALESCE(sum(CASE dd.tax WHEN 40 THEN dd.taxable ELSE 0 END ),0)  as cesstaxable,

             COALESCE(sum(CASE WHEN dd.tax=0 or dd.tax is null THEN dd.total_am ELSE 0 END ),0)  as sale0,
            COALESCE(sum(CASE WHEN dd.tax=1 THEN dd.total_am ELSE 0 END ),0)  as sale1,
	        COALESCE(sum(CASE dd.tax WHEN 5 THEN dd.total_am ELSE 0 END ),0)  as sale5,
            COALESCE(sum(CASE  WHEN dd.tax = 12 THEN dd.total_am ELSE 0 END ),0)  as sale12,
            COALESCE(sum(CASE dd.tax WHEN 18 THEN dd.total_am ELSE 0 END ),0)  as sale18,
            COALESCE(sum(CASE dd.tax WHEN 28 THEN dd.total_am ELSE 0 END ),0)  as sale28,
            COALESCE(sum(CASE dd.tax WHEN 40 THEN dd.total_am ELSE 0 END ),0)  as cesssale

            

            from
            (select ai.date_invoice,ai.number,ai.reference,
            round(ai.amount_untaxed,2) as total_taxable,round(ai.amount_tax,2) as total_tax,
            round(ai.amount_total,2) as total,
            round(sum((CASE WHEN ai.type = 'out_refund'  then  -1*ail.price_subtotal ELSE ail.price_subtotal END)),2) as taxable,
            
            round(sum(CASE WHEN ai.type = 'out_refund'  then  -1*ail.price_subtotal_taxinc ELSE ail.price_subtotal_taxinc END),2) as total_am,
            round(sum((CASE WHEN ai.type = 'out_refund'  then  -1*ail.price_subtotal_taxinc ELSE ail.price_subtotal_taxinc END)-
            (CASE WHEN ai.type = 'out_refund'  then  -1*ail.price_subtotal ELSE ail.price_subtotal END)),2) as tax_amount,at.amount as tax
            from account_invoice as ai
            left join account_invoice_line as ail on ail.invoice_id = ai.id
            left join account_invoice_line_tax as ailt
            on ailt.invoice_line_id=ail.id
            left join account_tax as at
            on at.id = ailt.tax_id
            left join stock_location as sl
            on (ai.stock_locations=sl.id) 

            where ai.date_invoice BETWEEN %s and %s and sl.id=%s and
            ai.state in ('open','paid')  and ai.type in ('out_invoice','out_refund')  
            group by at.id,ai.id)dd
            group by dd.date_invoice

                                                                               '''

        self.env.cr.execute(query21, (date_start,date_end,stock_location) )
        for row in self.env.cr.dictfetchall():
                # sl = sl + 1

                sale = 0
                possale = 0
                purtotal = 0

                # poscost = row['poscost'] if row['poscost'] else 0
                date_invoice = row['date_invoice'] if row['date_invoice'] else 0
                total_taxable = row['total_taxable'] if row['total_taxable'] else 0

                tax0 = row['tax0'] if row['tax0'] else 0
                tax1 = row['tax1'] if row['tax1'] else 0
                tax5 = row['tax5'] if row['tax5'] else 0
                tax12 = row['tax12'] if row['tax12'] else 0
                tax18 = row['tax18'] if row['tax18'] else 0
                tax28 = row['tax28'] if row['tax28'] else 0
                cesstax = row['cesstax'] if row['cesstax'] else 0


                sale0 = row['sale0'] if row['sale0'] else 0
                sale1 = row['sale1'] if row['sale1'] else 0
                sale5 = row['sale5'] if row['sale5'] else 0
                sale12 = row['sale12'] if row['sale12'] else 0
                sale18 = row['sale18'] if row['sale18'] else 0
                sale28 = row['sale28'] if row['sale28'] else 0
                cesssale = row['cesssale'] if row['cesssale'] else 0


                taxable0 = row['taxable0'] if row['taxable0'] else 0
                taxable1 = row['taxable1'] if row['taxable1'] else 0
                taxable5 = row['taxable5'] if row['taxable5'] else 0
                taxable12 = row['taxable12'] if row['taxable12'] else 0
                taxable18 = row['taxable18'] if row['taxable18'] else 0
                taxable28 = row['taxable28'] if row['taxable28'] else 0
                cesstaxable = row['cesstaxable'] if row['cesstaxable'] else 0

                total_tax = row['total_tax'] if row['total_tax'] else 0
                total= row['total'] if row['total'] else 0
                total_taxable = row['total_taxable'] if row['total_taxable'] else 0


                res = {
                    'cesstaxable':cesstaxable,
                    'cesssale':cesssale,
                    'cesstax':cesstax,
                    'date_invoice':date_invoice,
                    'total_taxable':total_taxable,
                    'sale0':sale0,
                    'sale1': sale1,
                    'sale5': sale5,
                    'sale12': sale12,
                    'sale18': sale18,
                    'sale28': sale28,

                    'taxable0': taxable0,
                    'taxable1': taxable1,
                    'taxable5': taxable5,
                    'taxable12': taxable12,
                    'taxable18': taxable18,
                    'taxable28': taxable28,

                    'tax0': tax0,
                    'tax1': tax1,
                    'tax5': tax5,
                    'tax12': tax12,
                    'tax18': tax18,
                    'tax28': tax28,

                    'total_tax':total_tax,
                    'total':total,
                    'total_taxable':total_taxable,

                    # 'sl_no': sl,

                }

                lines.append(res)

        if lines:
            return lines
        else:
            return []



    @api.model
    def render_html(self, docids, data=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        stock_location = data['form']['stock_location']
        stock_parent = self.env["stock.location"].browse(stock_location).location_id.name
        stock_name = self.env["stock.location"].browse(stock_location).name



        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()


        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        valueone = self.get_cash(data)

        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'date_end': date_object_date_end.strftime('%d-%m-%Y'),
            'data': data['form'],
            'time': time,
            # 'name_de':name_de,
            'data': data['form'],
            'doc_ids': self.ids,
            'data': data['form'],
            'doc_ids': self.ids,
            'valueone':valueone,
            'stock_location': stock_name,
            'stock_name': stock_parent,


            'time': time,


        }

        return self.env['report'].render('daily_tax_report.daily_report_pdf', docargs)
