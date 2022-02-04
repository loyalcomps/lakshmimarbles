# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportCategory(models.AbstractModel):

    _name = 'report.qlty_categorywise_xls.categorywise_report_pdf'

    def get_brand(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        category_id = data['form']['category_id']

        if category_id:
            sale_lines = self.env["pos.order.line"].search(
                [('order_id.date_order', '>=', date_start), ('order_id.date_order', '<=', date_end),
                 ('company_id', '=', company_id), ('product_id.categ_id', '=', category_id),
                 ('order_id.state', 'in', ['done', 'paid', 'invoiced'])])

            out_invoice_lines = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('invoice_id.type', '=', 'out_invoice'),
                 ('product_id.categ_id', '=', category_id),
                 ('invoice_id.state', 'in', ['open', 'paid'])])

            query1 = '''select * from account_invoice_line as ai
                    left join account_invoice as a
                    on a.id=ai.invoice_id
                    left join product_product as p
                    on ai.product_id =p.id
                    left join product_template as pt
                on pt.id = p.product_tmpl_id
                left join product_category as pc
                 on (pt.categ_id =pc.id)

                    where a.type='in_invoice' and a.state in ('open','paid') and pc.id= %s'''

            purchase_lines = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),
                 ('product_id.categ_id', '=', category_id), ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])
            product = self.env["product.product"].search([('categ_id', '=', category_id)])
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
            pf_amt = 0
            s_amt = 0
            s_qty = 0
            p_qty = 0
            profit = 0
            p_amt = 0
            price_u = 0

            cost = 0
            gross_profit = 0
            gross_profit_per = 0
            quantity = 0
            landingcost = 0

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
                left join product_category as pc
                 on (pt.categ_id =pc.id)

                where a.type in ('out_invoice','out_refund') and a.state in ('open','paid') and
                p.id = %s and a.company_id = %s and a.date_invoice BETWEEN %s and %s
                GROUP BY ai.product_id order by sale_qty'''
            self.env.cr.execute(sale_query, (i.id, company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                s_qty += row['sale_qty'] if row['sale_qty'] else 0
                s_amt += row['sale_amount'] if row['sale_amount'] else 0
                price_u += row['price_unit'] if row['price_unit'] else 0

            average_cost_query = '''select (SUM(ai.price_subtotal_taxinc)/SUM(ai.quantity)) as average_cost from account_invoice_line as ai
            left join account_invoice as a
            on a.id=ai.invoice_id
            left join product_product as p
            on ai.product_id =p.id
            left join product_template as pt
            on pt.id = p.product_tmpl_id
            left join product_category as pc
             on (pt.categ_id =pc.id)
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
                left join product_category as pc
                 on (pt.categ_id =pc.id)
                where a.type in ('in_invoice','in_refund') and a.state in ('open','paid') and
                            p.id = %s and a.company_id = %s and a.date_invoice BETWEEN %s and %s
                            GROUP BY ai.product_id'''
            self.env.cr.execute(purchase_query, (i.id, company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                p_qty += row['purchase_qty'] if row['purchase_qty'] else 0
                p_amt += row['purchase_amount'] if row['purchase_amount'] else 0
                pf_amt += row['purchase_freeqty'] if row['purchase_freeqty'] else 0

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
                left join product_category as pc
                 on (pt.categ_id =pc.id)
                where  a.state in ('done','paid','invoiced')  and
                            p.id = %s and a.company_id = %s and
                           to_char(date_trunc('day',a.date_order),'YYYY-MM-DD')::date between %s and %s

            '''
            self.env.cr.execute(offer_pricequery, (i.id, company_id, date_start, date_end,))
            for row in self.env.cr.dictfetchall():
                offer_price = row['offer'] if row['offer'] else 0

            query7 = '''
                                   SELECT pph.product_id as product_id ,pph.cost as cost,pph.id as id,pt.landing_cost as landingcost FROM 
                                                               product_price_history as pph 
                                                               left join product_product as pp on(pp.id=pph.product_id)
                                                               left join product_template as pt on(pt.id=pp.product_tmpl_id)
                                                               --left join product_category as pc on (pt.categ_id =pc.id)
                                                               WHERE pph.product_id = %s
                                               and pph.company_id = %s ORDER BY pph.id DESC LIMIT 1
                                               '''
            # query1 = '''
            # SELECT product_id,cost,id FROM product_price_history  WHERE product_id = %s and company_id = %s ORDER BY id DESC LIMIT 1
            # '''
            self.env.cr.execute(query7, (i.id, company_id

                                         ))
            for ans in self.env.cr.dictfetchall():
                cost = ans['cost'] if ans['cost'] else 0
                landingcost = ans['landingcost'] if ans['landingcost'] else 0
            if not cost:
                query2 = '''
                                           select sum(mrp_bom_line.product_qty) as product_qty,mrp_bom_line.product_id
                                           from mrp_bom_line 
                                           left join mrp_bom on mrp_bom.id = mrp_bom_line.bom_id
                                           left join product_template on product_template.id = mrp_bom.product_tmpl_id
                                           left join product_product on product_product.product_tmpl_id = product_template.id
                                           --left join product_category as pc on (product_template.categ_id =pc.id)
                                           where product_product.id = %s and mrp_bom.company_id = %s
                                           group by mrp_bom_line.product_id
                                       '''
                self.env.cr.execute(query2, (i.id, company_id

                                             ))
                for answer in self.env.cr.dictfetchall():
                    quantity = answer['product_qty'] if answer['product_qty'] else 0
                    query3 = ''' 
                                               SELECT pph.product_id as product_id ,pph.cost as cost,pph.id as id,pt.landing_cost as landingcost FROM 
                                                               product_price_history as pph 
                                                               left join product_product as pp on(pp.id=pph.product_id)
                                                               left join product_template as pt on(pt.id=pp.product_tmpl_id)
                                                               --left join product_category as pc on (pt.categ_id =pc.id)
                                                               WHERE pph.product_id = %s
                                               and pph.company_id = %s ORDER BY pph.id DESC LIMIT 1
                                            '''
                    self.env.cr.execute(query3, (answer['product_id'], company_id

                                                 ))
                    for answer1 in self.env.cr.dictfetchall():
                        cost = answer1['cost'] if answer1['cost'] else 0
                        landingcost = answer1['landingcost'] if answer1['landingcost'] else 0

            res = {
                'sl_no': sl,
                'product': i.name,
                'category': i.categ_id.name,
                'onhand': i.qty_available,
                's_qty': s_qty,
                'sale': s_amt,
                'sale_price': i.lst_price,
                'p_qty': p_qty + pf_amt,
                'purchase': p_amt,
                'profit': round((s_amt - (average_cost * s_qty)), 2),
                'landing_cost': i.product_tmpl_id.landing_cost,
                'margin': (i.product_mrp) - (i.product_tmpl_id.landing_cost),
                'offer_price': offer_price,
                'price_unit': price_u,
                'cost': (cost * quantity) if quantity else (cost),
                'average_cost': average_cost
            }

            lines.append(res)

        if lines:
            return sorted(lines, key=lambda i: (i['profit'], i['sale']), reverse=True)
        else:
            return []

    @api.model
    def render_html(self, docids, data=None, config_id=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        category_id = data['form']['category_id']

        category_id = data['form']['category_id']
        category_name = self.env["product.category"].browse(category_id).name

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
            # 'config': config,
            # 'configures': configures,
            'data': data['form'],
            'doc_ids': self.ids,
            'data': data['form'],
            'doc_ids': self.ids,

            # 'get_lines': get_lines if get_lines else 0,
            # 'get_brand': get_brand if get_brand else 0,
            'category_name': category_name,

        }

        return self.env['report'].render('qlty_categorywise_xls.categorywise_report_pdf', docargs)
