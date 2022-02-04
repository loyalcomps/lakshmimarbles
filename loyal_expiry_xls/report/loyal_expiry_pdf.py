# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Reportbrand(models.AbstractModel):
        _name = 'report.loyal_expiry_xls.expiry_report_pdf'

        def get_sale(self, data):
            lines = []
            res = {}
            date_start = data['form']['date_start']
            date_end = data['form']['date_end']
            sl=0
            company_id = data['form']['company_id']

            query='''
               select max(p.name) as pname,max(p.expiry_date) as expiry,sum(sh.quantity) as quantity,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation
                from stock_history sh left join product_template p on (p.id = sh.product_template_id) where date <= %s and
                 p.expiry_date between %s and %s and sh.company_id=%s
                and available_in_pos = True group by sh.product_id  order by max(p.expiry_date)


                    '''


            self.env.cr.execute(query, (date_start,date_start,date_end,company_id))
            for row in self.env.cr.dictfetchall():
                sl=sl+1
                dates = datetime.strptime(row['expiry'], '%Y-%m-%d').date()

                res = {
                        'sl':sl ,
                        'date':  dates.strftime('%d-%m-%Y'),
                        'pname': row['pname'],
                        'quantity': row['quantity'],
                        'valuation': row['valuation'],


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
            sale = self.get_sale(data)

            date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
            date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

            docargs = {
                'doc_ids': self.ids,
                'date_start':date_object_date_start.strftime('%d-%m-%Y'),
                'date_end':date_object_date_end.strftime('%d-%m-%Y'),
                'sale':sale,

            }

            return self.env['report'].render('loyal_expiry_xls.expiry_report_pdf', docargs)
