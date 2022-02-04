from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime

from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from odoo import models, fields, api,_
import time
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta



class Qltyvendorwisepdfbrand(models.AbstractModel):
    _name ='report.brandwise_report_pdf.qlty_brand_pdf'

    def get_brand(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        brand_id= data['form']['brand_id']

        if brand_id:
            sale_lines = self.env["pos.order.line"].search(
                [('order_id.date_order', '>=', date_start), ('order_id.date_order', '<=', date_end),
                 ('company_id', '=', company_id), ('product_id.brand_id', '=', brand_id),
                 ('order_id.state', 'in', ['done', 'paid', 'invoiced'])])

            out_invoice_lines = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('invoice_id.type', '=', 'out_invoice'),
                 ('product_id.brand_id', '=', brand_id),
                 ('invoice_id.state', 'in', ['open', 'paid'])])

            query1 = '''select * from account_invoice_line as ai
                    left join account_invoice as a
                    on a.id=ai.invoice_id
                    left join product_product as p
                    on ai.product_id =p.id
                    left join product_brand as pb 
                    on pb.id=p.brand_id
                    
                    where a.type='in_invoice' and a.state in ('open','paid') and p.brand_id = %s'''

            purchase_lines = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('product_id.brand_id', '=', brand_id), ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])
            product = self.env["product.product"].search([('brand_id', '=', brand_id)])
        else:
            sale_lines = self.env["pos.order.line"].search(
                [('order_id.date_order', '>=', date_start), ('order_id.date_order', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('order_id.state', 'in', ['done', 'paid', 'invoiced'])])
            out_invoice_lines = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id), ('invoice_id.type', '=', 'out_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])

            purchase_lines_total = self.env["account.invoice.line"].search(
                [('company_id', '=', company_id),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])

            purchase_lines = self.env["account.invoice.line"].search([('invoice_id.type', '=', 'in_invoice'),
                                                                      ('invoice_id.date_invoice', '>=', date_start),
                                                                      ('invoice_id.date_invoice', '<=', date_end),
                                                                      ('company_id', '=', company_id),
                                                                      ('invoice_id.state', 'in', ['open', 'paid'])])
            product = self.env["product.product"].search([])

        sl = 0
        for i in product:
            pf_amt=0
            s_amt = 0
            s_qty = 0
            p_qty = 0
            profit = 0
            p_amt = 0
            price_u=0
            sl += 1
            sale_query = ''' select SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.quantity  ELSE ai.quantity END) as sale_qty,
            SUM(CASE WHEN a.type = 'out_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END) as sale_amount,
            max(ai.price_unit) as price_unit,
            product_id from account_invoice_line as ai
                left join account_invoice as a
                on a.id=ai.invoice_id
                left join product_product as p
                on ai.product_id =p.id
                left join product_template as pt
                on pt.id = p.product_tmpl_id
                left join product_brand as pb 
                on pb.id=p.brand_id
                
                where a.type in ('out_invoice','out_refund') and a.state in ('open','paid') and
                p.id = %s and a.company_id = %s and a.date_invoice BETWEEN %s and %s
                GROUP BY ai.product_id order by sale_qty'''
            self.env.cr.execute(sale_query, (i.id, company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                s_qty += row['sale_qty'] if row['sale_qty'] else 0
                s_amt += row['sale_amount'] if row['sale_amount'] else 0
                price_u +=row['price_unit'] if row['price_unit'] else 0



            average_cost_query = '''select SUM(ai.price_subtotal_taxinc/ai.quantity) as average_cost from account_invoice_line as ai
            left join account_invoice as a
            on a.id=ai.invoice_id
            left join product_product as p
            on ai.product_id =p.id
            left join product_template as pt
            on pt.id = p.product_tmpl_id
            left join product_brand as pb 
                    on pb.id=p.brand_id
            where a.type='in_invoice' and a.state in ('open','paid') and p.id = %s and a.company_id = %s
            '''
            self.env.cr.execute(average_cost_query, (i.id, company_id,))
            for row in self.env.cr.dictfetchall():
                average_cost = row['average_cost'] if row['average_cost'] else 0
            purchase_query = ''' 
            select SUM(CASE WHEN a.type = 'in_refund'  then  -1*ai.quantity  ELSE ai.quantity END ) as purchase_qty,
                     SUM(CASE WHEN a.type = 'in_refund'  then  -1*ai.free_qty  ELSE ai.free_qty END ) as purchase_freeqty,
            SUM(CASE WHEN a.type = 'in_refund'  then  -1*ai.price_subtotal_taxinc ELSE ai.price_subtotal_taxinc END ) as purchase_amount,
            product_id from account_invoice_line as ai
                left join account_invoice as a
                on a.id=ai.invoice_id
                left join product_product as p
                on ai.product_id =p.id
                left join product_template as pt
                on pt.id = p.product_tmpl_id
                left join product_brand as pb 
                    on pb.id=p.brand_id
                where a.type in ('in_invoice','in_refund') and a.state in ('open','paid') and
                            p.id = %s and a.company_id = %s and a.date_invoice BETWEEN %s and %s
                            GROUP BY ai.product_id'''
            self.env.cr.execute(purchase_query, (i.id, company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                p_qty += row['purchase_qty'] if row['purchase_qty'] else 0
                p_amt += row['purchase_amount'] if row['purchase_amount'] else 0
                pf_amt+= row['purchase_freeqty'] if row['purchase_freeqty'] else 0

            offer_price = 0
            offer_pricequery = '''
                select ai.price_unit as offer,ai.product_id from pos_order_line as ai
                left join pos_order as a
                on a.id=ai.order_id
                left join product_pricelist as ppr
                on ppr.id=a.pricelist_id
                left join pos_config as poc
                on poc.pricelist_id=ppr.id
                left join product_product as p
                on ai.product_id =p.id
                left join product_template as pt
                on pt.id = p.product_tmpl_id
                left join product_brand as pb 
                    on pb.id=p.brand_id
                where  a.state in ('done','paid','invoiced')  and
                            p.id = %s and a.company_id = %s and
                           to_char(date_trunc('day',a.date_order),'YYYY-MM-DD')::date between %s and %s

            '''
            self.env.cr.execute(offer_pricequery, (i.id, company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                offer_price = row['offer'] if row['offer'] else 0


            res = {
                'sl_no': sl,
                'product': i.name,
                'category': i.categ_id.name,
                'onhand': i.qty_available,
                's_qty': s_qty,
                'sale': s_amt,
                'sale_price': i.lst_price,
                'p_qty': p_qty+pf_amt,
                'purchase': p_amt,
                'profit': round((s_amt - (average_cost * s_qty)), 2),
                'landing_cost': i.product_tmpl_id.landing_cost,
                'margin': (i.product_mrp) - (i.product_tmpl_id.landing_cost),
                'offer_price': offer_price,
                'price_unit':price_u
            }

            lines.append(res)

        if lines:
            return sorted(lines, key = lambda i: (i['s_qty'],i['p_qty']),reverse=True)
        else:
            return []

    @api.model
    def render_html(self, docids, data=None, config_id=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        category_id = data['form']['category_id']
        brand_id = data['form']['brand_id']
        brand_only = data['form']['brand_only']
        category_id = data['form']['category_id']
        category_name = self.env["product.category"].browse(category_id).name
        brand_name = self.env["product.brand"].browse(brand_id).name

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        get_brand = self.get_brand(data)


        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'date_end': date_object_date_end.strftime('%d-%m-%Y'),
            'category_name': category_name if category_name else 'All Category Report',
            'data': data['form'],
            'time': time,
            'valuesone': get_brand,
            'brand_only': brand_only,
            # 'config': config,
            # 'configures': configures,
            'data': data['form'],
            'doc_ids': self.ids,
            'data': data['form'],
            'brand_id': brand_id,
            'doc_ids': self.ids,

            # 'get_lines': get_lines if get_lines else 0,
            # 'get_brand': get_brand if get_brand else 0,
            'category_name': category_name,
            'brand_name': brand_name

        }


        return self.env['report'].render('brandwise_report_pdf.qlty_brand_pdf', docargs)