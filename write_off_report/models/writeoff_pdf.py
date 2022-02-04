# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Inventoryreport(models.AbstractModel):

    _name = 'report.write_off_report.writeoff_report_pdf'

    def get_product(self, data):

        lines = []
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']
        product_id = data['form']['product_id']

        query = '''select pp.barcode,pt.name,sm.onhand_qty,(sm.onhand_qty*sm.price_unit) as value,
                    sm.product_uom_qty as scrap_qty,(sm.product_uom_qty*sm.price_unit) as scrap_value,
                    (sm.onhand_qty-sm.product_uom_qty) as ext_qty, 
                    ((sm.onhand_qty-sm.product_uom_qty)*sm.price_unit) as ext_value from stock_move sm
                    left join product_product as pp on pp.id=sm.product_id
                    left join product_template as pt on pt.id=pp.product_tmpl_id

                    where sm.scrapped= true and sm.location_id =%s and sm.company_id=%s and sm.state ='done'
                    and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date = %s and pp.id=%s'''

        sl = 0
        self.env.cr.execute(query, (stock_location, company_id, date_start, product_id))
        for row in self.env.cr.dictfetchall():
            sl += 1
            barcode = row['barcode'] if row['barcode'] else 0
            name = row['name'] if row['name'] else 0
            opening_stock = row['onhand_qty'] if row['onhand_qty'] else 0
            current_system_stock = row['value'] if row['value'] else 0
            trans_qty = row['scrap_qty'] if row['scrap_qty'] else 0
            trans_val = row['scrap_value'] if row['scrap_value'] else 0
            closing_stock = row['ext_qty'] if row['ext_qty'] else 0
            current_val = row['ext_value'] if row['ext_value'] else 0

            res = {
                'sl': sl,
                'barcode': barcode,
                'product': name,
                'opening_stock': round(opening_stock,2),
                'current_system_stock': round(current_system_stock,2),
                'transferred_qty': round(trans_qty,2),
                'transferred_value': round(trans_val,2),
                'current_value': round(current_val,2),
                'closing_stock': round(closing_stock,2),

            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_product_location(self, data):

        lines = []
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']

        query = '''select pp.barcode,pt.name,sm.onhand_qty,(sm.onhand_qty*sm.price_unit) as value,
            sm.product_uom_qty as scrap_qty,(sm.product_uom_qty*sm.price_unit) as scrap_value,
            (sm.onhand_qty-sm.product_uom_qty) as ext_qty, 
            ((sm.onhand_qty-sm.product_uom_qty)*sm.price_unit) as ext_value from stock_move sm
            left join product_product as pp on pp.id=sm.product_id
            left join product_template as pt on pt.id=pp.product_tmpl_id

            where sm.scrapped= true and sm.location_id =%s and sm.company_id=%s and sm.state ='done'
            and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date = %s  '''

        sl = 0
        self.env.cr.execute(query, (stock_location, company_id, date_start))
        for row in self.env.cr.dictfetchall():
            sl += 1
            barcode = row['barcode'] if row['barcode'] else 0
            name = row['name'] if row['name'] else 0
            opening_stock = row['onhand_qty'] if row['onhand_qty'] else 0
            current_system_stock = row['value'] if row['value'] else 0
            trans_qty = row['scrap_qty'] if row['scrap_qty'] else 0
            trans_val = row['scrap_value'] if row['scrap_value'] else 0
            closing_stock = row['ext_qty'] if row['ext_qty'] else 0
            current_val = row['ext_value'] if row['ext_value'] else 0

            res = {
                'sl': sl,
                'barcode': barcode,
                'product': name,
                'opening_stock': round(opening_stock,2),
                'current_system_stock': round(current_system_stock,2),
                'transferred_qty': round(trans_qty,2),
                'transferred_value': round(trans_val,2),
                'current_value': round(current_val,2),
                'closing_stock': round(closing_stock,2),

            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_line(self, data):

        lines = []
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']
        category_id = data['form']['category_id']
        product_id = data['form']['product_id']

        cr = 0

        query = '''select pp.barcode,pt.name,sm.onhand_qty,(sm.onhand_qty*sm.price_unit) as value,
                            sm.product_uom_qty as scrap_qty,(sm.product_uom_qty*sm.price_unit) as scrap_value,
                            (sm.onhand_qty-sm.product_uom_qty) as ext_qty, 
                            ((sm.onhand_qty-sm.product_uom_qty)*sm.price_unit) as ext_value from stock_move sm
                            left join product_product as pp on pp.id=sm.product_id
                            left join product_template as pt on pt.id=pp.product_tmpl_id

                            where sm.scrapped= true and sm.location_id =%s and sm.company_id=%s and sm.state ='done'
                            and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date = %s and pp.id=%s and pt.categ_id=%s'''

        sl = 0
        self.env.cr.execute(query, (stock_location, company_id, date_start, product_id, category_id))
        for row in self.env.cr.dictfetchall():
            sl += 1
            barcode = row['barcode'] if row['barcode'] else 0
            name = row['name'] if row['name'] else 0
            opening_stock = row['onhand_qty'] if row['onhand_qty'] else 0
            current_system_stock = row['value'] if row['value'] else 0
            trans_qty = row['scrap_qty'] if row['scrap_qty'] else 0
            trans_val = row['scrap_value'] if row['scrap_value'] else 0
            closing_stock = row['ext_qty'] if row['ext_qty'] else 0
            current_val = row['ext_value'] if row['ext_value'] else 0

            res = {
                'sl': sl,
                'barcode': barcode,
                'product': name,
                'opening_stock': round(opening_stock,2),
                'current_system_stock': round(current_system_stock,2),
                'transferred_qty': round(trans_qty,2),
                'transferred_value': round(trans_val,2),
                'current_value': round(current_val,2),
                'closing_stock': round(closing_stock,2)

            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_product_category(self, data):

        lines = []

        date_start = data['form']['date_start']
        company_id = data['form']['company_id']
        stock_location = data['form']['stock_location']
        category_id = data['form']['category_id']

        query = '''select pp.barcode,pt.name,sm.onhand_qty,(sm.onhand_qty*sm.price_unit) as value,
                    sm.product_uom_qty as scrap_qty,(sm.product_uom_qty*sm.price_unit) as scrap_value,
                    (sm.onhand_qty-sm.product_uom_qty) as ext_qty, 
                    ((sm.onhand_qty-sm.product_uom_qty)*sm.price_unit) as ext_value from stock_move sm
                    left join product_product as pp on pp.id=sm.product_id
                    left join product_template as pt on pt.id=pp.product_tmpl_id

                    where sm.scrapped= true and sm.location_id =%s and sm.company_id=%s and sm.state ='done'
                    and to_char(date_trunc('day',sm.date),'YYYY-MM-DD')::date = %s  and pt.categ_id=%s'''

        sl = 0
        self.env.cr.execute(query, (stock_location, company_id, date_start, category_id))
        for row in self.env.cr.dictfetchall():
            sl += 1
            barcode = row['barcode'] if row['barcode'] else 0
            name = row['name'] if row['name'] else 0
            opening_stock = row['onhand_qty'] if row['onhand_qty'] else 0
            current_system_stock = row['value'] if row['value'] else 0
            trans_qty = row['scrap_qty'] if row['scrap_qty'] else 0
            trans_val = row['scrap_value'] if row['scrap_value'] else 0
            closing_stock = row['ext_qty'] if row['ext_qty'] else 0
            current_val = row['ext_value'] if row['ext_value'] else 0

            res = {
                'sl': sl,
                'barcode': barcode,
                'product': name,
                'opening_stock': round(opening_stock,2),
                'current_system_stock': round(current_system_stock,2),
                'transferred_qty': round(trans_qty,2),
                'transferred_value': round(trans_val,2),
                'current_value': round(current_val,2),
                'closing_stock': round(closing_stock,2)

            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []
    @api.model
    def render_html(self, docids, data=None):

        date_start = data['form']['date_start']
        company_id = data['form']['company_id']
        category_id = data['form']['category_id']
        product_id = data['form']['product_id']

        stock_location = data['form']['stock_location']
        stock_parent = self.env["stock.location"].browse(stock_location).location_id.name
        stock_name = self.env["stock.location"].browse(stock_location).name
        location =stock_parent+"/"+stock_name
        category_name =self.env["product.category"].browse(category_id).name

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        if category_id==False and product_id==False:
            result = self.get_product_location(data)
        if product_id==False and category_id:
            result = self.get_product_category(data)
        if product_id and category_id == False:
            result = self.get_product(data)
        if product_id and category_id:
            result = self.get_line(data)


        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'data': data['form'],
            'category_id': category_id,
            'product_id': product_id,
            'category_name':category_name,
            'stock_location': location,
            'result':result if result else [],

        }

        return self.env['report'].render('write_off_report.writeoff_report_pdf', docargs)
