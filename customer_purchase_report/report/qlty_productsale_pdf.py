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
    _name='report.customer_purchase_report.customerpurchase_report_pdf'

    def get_purchase(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']

        sl = 0
        if counter_only:

            # query='''
            #
            # select res.name as name,
            # res.phone as phone,
            # res.mobile as mobile,
            # count(ai.number) as count,
            # max(ai.date_invoice) as date
			 # from res_partner as res
				# left join account_invoice as ai on(res.id=ai.partner_id)
            #
			 # where res.id not in(select ai.partner_id from account_invoice as ai
				# left join account_invoice_line as ail on (ai.id=ail.invoice_id)
				# left join res_partner as res on(res.id=ai.partner_id)
            #
				#  where
            #
				#  ai.type='out_invoice' and ai.state in ('open','paid') and
            #                  ai.date_invoice BETWEEN %s and %s and ai.company_id = %s
            #                group by ai.partner_id ) group by res.id order by res.name
            #
            #
            #
            # '''
            query = '''

          select res.name as name,
                res.phone as phone,
                count(po.pos_reference) as count,
                cast(max(po.date_order) as date),
                --max(po.date_order) as date,
                res.mobile as mobile
                 from res_partner as res
                 left join pos_order as po on(res.id=po.partner_id)
                  where res.id not in(select po.partner_id from pos_order as po
                    left join pos_order_line as pol on (po.id=pol.order_id)
                    left join res_partner as res on(res.id=po.partner_id)

                     where
                    po.state in  ('done', 'paid','invoiced')
                    and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
                    and pol.company_id= %s group by po.partner_id ) and res.customer = True group by res.id order by res.name
                    '''

            self.env.cr.execute(query, (
                date_start, date_end, company_id
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1

                ppname = row['name'] if row['name'] else " "
                phone = row['phone'] if row['phone'] else " "
                mobile = row['mobile'] if row['mobile'] else " "
                count = row['count'] if row['count'] else " "
                # dates = datetime.strptime(row['date'], '%Y-%m-%d').date()
                # if row['date']:
                #    dates = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S').date()
                # else:
                #     dates = '--'
                dates = row['max'] if row['max'] else " "
                # purchasetotal = row['total'] if row['total'] else 0
                # purchaseqty = row['qty'] if row['qty'] else 0

                res = {
                    'sl_no': sl,
                    'ppname': ppname,
                    'purchasedate':dates if dates else " ",
                    'purchasetotal': 0.0,
                    'purchaseqty': 0.0,
                    'phone': phone if phone else mobile,
                    'mobile': mobile,
                    'count':count

                }

                lines.append(res)

            if lines:
                return lines
            else:
                return []

    def get_lines(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        counter_only = data['form']['counter_only']

        sl = 0

        # query='''
        # select  res.name as name,
			# 	res.phone as phone,
			# 	res.mobile as mobile,
			# 	count(ai.number) as count,
			# 	max(ai.date_invoice) as date,
			# 	round(sum((ail.quantity))) as qty,
			# 	round(sum(ail.price_subtotal_taxinc)) as total
        #
			#
			#
        #                 from account_invoice as ai
			# 	left join account_invoice_line as ail on (ai.id=ail.invoice_id)
			# 	left join res_partner as res on(res.id=ai.partner_id)
        #                 where
			# 	ai.type='out_invoice' and ai.state in ('open','paid') and
        #                      ai.date_invoice BETWEEN %s and %s and ai.company_id = %s
        #                       group by res.id order by total DESC
        #
        # '''
        query = '''

   select  res.name as name,
				res.phone as phone,
				res.mobile as mobile,
				count(distinct(po.id)) as count,
				--max(po.date_order) as date,
				cast(max(po.date_order) as date),
				round(sum((pol.qty))) as qty,
				round(sum((pol.qty * pol.price_unit) * (1 - (pol.discount) / 100.0)),2) as total



                        from pos_order as po
				left join pos_order_line as pol on (po.id=pol.order_id)
				left join res_partner as res on(res.id=po.partner_id)

                        where
				po.state in  ('done', 'paid','invoiced')
				and  to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date between %s and %s
				and pol.company_id= %s and res.customer = True group by res.id order by total DESC
            '''

        self.env.cr.execute(query, (
            date_start, date_end, company_id
        ))
        for row in self.env.cr.dictfetchall():
            sl += 1

            ppname = row['name'] if row['name'] else " "
            phone = row['phone'] if row['phone'] else " "
            mobile = row['mobile'] if row['mobile'] else " "
            count = row['count'] if row['count'] else " "

            # dates = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S').date()
            dates = row['max'] if row['max'] else " "

            # purchasedate = row['date'] if row['date'] else " "
            purchasetotal = row['total'] if row['total'] else 0
            purchaseqty = row['qty'] if row['qty'] else 0


            res = {
                'sl_no': sl,
                'ppname': ppname,
                'purchasedate': dates if dates else " ",
                'purchasetotal': purchasetotal,
                'purchaseqty': purchaseqty,
                'phone':phone if phone else mobile,
                'mobile':mobile,
                'count': count


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
        counter_only = data['form']['counter_only']
        get_lines = self.get_lines(data)
        get_purchase = self.get_purchase(data)

        date_object_startdate = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_enddate = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'counter_only':counter_only,
            'doc_ids': self.ids,
            'date_start': date_object_startdate.strftime('%d-%m-%Y'),
            'date_end': date_object_enddate.strftime('%d-%m-%Y'),

            'data': data['form'],
            'get_lines': get_lines,
            'get_purchase':get_purchase
        }

        return self.env['report'].render('customer_purchase_report.customerpurchase_report_pdf', docargs)
