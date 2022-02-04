# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Reportdeadstock(models.AbstractModel):

    _name = 'report.seven_deadstock_xls.seven_deadstock_pdf'

    # def get_lines(self, data):
    #
    #     lines = []
    #     res = {}
    #     val = {}
    #     inv = []
    #
    #     date_start = data['form']['date_start']
    #     date_end = data['form']['date_end']
    #     company_id = data['form']['company_id']
    #     wh_id = data['form']['wh_id']
    #     min_qty = data['form']['min_qty']
    #     product = self.env['product.product'].search([('qty_available', '>', 0)])
    #
    #     if wh_id:
    #         sale = self.env['pos.order.line'].search(
    #             [('order_id.date_order', '>=', date_start), ('order_id.date_order', '<=', date_end),
    #              ('company_id', '=', company_id), ('order_id.picking_type_id ', '=', wh_id),
    #              ('order_id.state', 'in', ['paid', 'done', 'invoiced'])])
    #
    #     else:
    #         sale = self.env['pos.order.line'].search(
    #             [('order_id.date_order', '>=', date_start), ('order_id.date_order', '<=', date_end),
    #              ('company_id', '=', company_id), ('order_id.state', 'in', ['paid', 'done', 'invoiced'])])
    #
    #     for pdct in product:
    #         sl = 0
    #         for line in sale:
    #             if pdct.id == line.product_id:
    #                 sl += 1
    #         if sl <= min_qty:
    #             res = {
    #                 'product': pdct.name,
    #                 'barcode': pdct.barcode,
    #                 'brand': pdct.brand_id.name,
    #                 'qty': pdct.qty_available,
    #                 'trp': pdct.lst_price,
    #                 'total': pdct.qty_available * pdct.lst_price,
    #
    #             }
    #             lines.append(res)
    #
    #     if lines:
    #         return lines
    #     else:
    #         return []

    def get_lines(self, data):

        lines = []
        res = {}
        val = {}
        inv = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        wh_id = data['form']['wh_id']
        min_qty = data['form']['min_qty']
        sl = 0

        query = '''  select (pp.id),pp.barcode as barcode,pp.brand_id as brand,sum(sh.quantity) as qty,pt.list_price as sale_price,
sum(sh.quantity)*pt.list_price as tamount,
max(pt.name) as product,max(pb.name) as brandname from product_product as pp
		left join stock_history as sh on(pp.id=sh.product_id)
		left join product_template pt on (pt.id=pp.product_tmpl_id)
		left join product_brand as pb on (pb.id=pp.brand_id) 
             
 where 
 sh.quantity>0 and
 pp.id not in(select pol.product_id from pos_order_line as pol
					left join pos_order as po on(po.id=pol.order_id)
					left join product_product as pp on (pp.id=pol.product_id)
					left join product_template as pt on (pt.id=pp.product_tmpl_id)

					where to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date 
                            between %s and %s and  po.state IN ('done', 'paid', 'invoiced') 
				and po.company_id=%s group by pol.product_id
					) group by pp.id,pt.list_price,pt.name order by pt.name ASC
                                    '''
        self.env.cr.execute(query, (date_start, date_end, company_id,))

        for row in self.env.cr.dictfetchall():
            sl += 1
            productname = row['product'] if row['product'] else 0
            quantity = row['qty'] if row['qty'] else 0
            barcode = row['barcode'] if row['barcode'] else 0
            brand = row['brandname'] if row['brandname'] else 0
            sale_price = row['sale_price'] if row['sale_price'] else 0
            tamount = row['tamount'] if row['tamount'] else 0
            sl += 1

            res = {

                'sl_no': sl if sl else 0,

                'product': productname,
                # 'quantity': quantity,
                'barcode': barcode,
                'brand': brand,
                'qty': quantity,
                'trp': sale_price,
                'total': tamount,

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
        company_id = data['form']['company_id']
        wh_id = data['form']['wh_id']
        min_qty = data['form']['min_qty']
        valuesone = self.get_lines(data)
        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'date_end': date_object_date_end.strftime('%d-%m-%Y'),

            'data': data['form'],
            'time': time,
            'valuesone': valuesone,
        }

        return self.env['report'].render('seven_deadstock_xls.seven_deadstock_pdf', docargs)
