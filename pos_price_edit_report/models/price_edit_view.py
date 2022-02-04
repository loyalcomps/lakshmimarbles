# -*- coding: utf-8 -*-

import time
from openerp import api, models, _
from openerp.exceptions import UserError
from openerp.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time


class Reportbrand(models.AbstractModel):

    _name = 'report.pos_price_edit_report.pos_price_edit_report_view'


    def get_data(self, data):
        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        pos_config_ids = data['form']['pos_config_ids']
        if pos_config_ids:
            config_ids = tuple(pos_config_ids)
        else:
            config_ids=[]
            query = """select id from pos_config"""
            self.env.cr.execute(query)
            for row in self.env.cr.dictfetchall():
                config_ids.append(row['id'])
            config_ids=tuple(config_ids)

        company_id = data['form']['company_id']
        user_id = data['form']['user_id']
        if user_id:
            users_id = []
            users_id.append(user_id)
            user_id = tuple(users_id)
        else:
            user_id = []
            query = """select id from res_users"""
            self.env.cr.execute(query)
            for row in self.env.cr.dictfetchall():
                user_id.append(row['id'])
            user_id = tuple(user_id)
            # user_id = tuple(lambda self: self.env['res.users'].search([]))
        product_id = data['form']['product_id']
        if product_id:
            products_id = []
            products_id.append(product_id)
            product_id = tuple(products_id)
        else:
            product_id = []
            query = """select id from product_product"""
            self.env.cr.execute(query)
            for row in self.env.cr.dictfetchall():
                product_id.append(row['id'])
            product_id = tuple(product_id)
            # product_id = '''(select id from product_product)'''

        query = """
        
        
        select users.id as user,config.name as config,template.name as product,
            pol.qty,pol.product_mrp,pol.actual_price,po.name as order_ref,po.pos_reference as receipt_ref,
            pol.price_unit,pol.create_date from pos_order_line pol
            left join pos_order po on po.id=pol.order_id
            left join pos_session session on session.id =po.session_id
            left join pos_config config on config.id = session.config_id
            left join res_users users on users.id=po.user_id
            left join product_product product on product.id=pol.product_id
            left join product_template template on template.id = product.product_tmpl_id
            left join product_category as pc on template.categ_id =pc.id
            where pol.actual_price!=pol.price_unit and to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date
            between %s AND %s 
            --and po.pricelist_id=config.pricelist_id
            and pol.id not in (select pol.id from pos_order_line pol
            left join pos_order po on po.id=pol.order_id
            left join pos_session session on session.id =po.session_id
            left join pos_config config on config.id = session.config_id
            left join res_users users on users.id=po.user_id
            left join product_product product on product.id=pol.product_id
            left join product_template template on template.id = product.product_tmpl_id
            left join product_category as pc on template.categ_id =pc.id
            left join product_pricelist_item as ppi on ppi.pricelist_id=po.pricelist_id
            where pol.actual_price!=pol.price_unit and to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date
            between %s AND %s
            and po.pricelist_id<>config.pricelist_id and ppi.product_tmpl_id=product.product_tmpl_id
            )


            and pol.id not in (select pol.id from pos_order_line pol
            left join pos_order po on po.id=pol.order_id
            left join pos_session session on session.id =po.session_id
            left join pos_config config on config.id = session.config_id
            left join res_users users on users.id=po.user_id
            left join product_product product on product.id=pol.product_id
            left join product_template template on template.id = product.product_tmpl_id
            left join product_category as pc on template.categ_id =pc.id
            left join product_pricelist_item as ppi on ppi.pricelist_id=po.pricelist_id
            where pol.actual_price!=pol.price_unit and to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date
            between %s AND %s 
            and po.pricelist_id<>config.pricelist_id and ppi.product_id=product.id
            ) 
             and pol.id not in (select pol.id from pos_order_line pol
            left join pos_order po on po.id=pol.order_id
            left join pos_session session on session.id =po.session_id
            left join pos_config config on config.id = session.config_id
            left join res_users users on users.id=po.user_id
            left join product_product product on product.id=pol.product_id
            left join product_template template on template.id = product.product_tmpl_id
            left join product_category as pc on template.categ_id =pc.id
            left join product_pricelist_item as ppi on ppi.pricelist_id=po.pricelist_id
            where pol.actual_price!=pol.price_unit and to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date
            between %s AND %s
            and po.pricelist_id<>config.pricelist_id and ppi.categ_id=pc.id
            ) 
            and  pol.id not in (select pol.id from pos_order_line pol
            left join pos_order po on po.id=pol.order_id
            left join pos_session session on session.id =po.session_id
            left join pos_config config on config.id = session.config_id
            left join res_users users on users.id=po.user_id
            left join product_product product on product.id=pol.product_id
            left join product_template template on template.id = product.product_tmpl_id
            left join product_category as pc on template.categ_id =pc.id
            left join product_pricelist_item as ppi on ppi.pricelist_id=po.pricelist_id
            where pol.actual_price!=pol.price_unit and to_char(date_trunc('day',po.date_order),'YYYY-MM-DD')::date
            between %s AND %s
            and po.pricelist_id<>config.pricelist_id and ppi.applied_on='3_global')
            and users.id in %s
            and product.id in %s and config.id in %s
             and po.company_id =%s"""

        self.env.cr.execute(query, (date_start, date_end,
                                    date_start, date_end,
                                    date_start, date_end,
                                    date_start, date_end,
                                    date_start, date_end,
                                    user_id,product_id,config_ids,company_id))
        for row in self.env.cr.dictfetchall():
            order_ref=row['order_ref'] if row['order_ref'] else ""
            receipt_ref=row['receipt_ref'] if row['receipt_ref'] else ""
            if row['create_date']:
                createdatetime = row['create_date']
                x = time.strptime(createdatetime.split('.')[0], '%Y-%m-%d %H:%M:%S')
                x = time.strftime('%Y-%m-%d %H:%M:%S', x)
            else:
                x=""


            res = {
                'user': self.env['res.users'].browse(row['user']).name,
                'config': row['config'],
                'product': row['product'],
                'qty': round(row['qty'],2) if row['qty'] else 0,
                'product_mrp': round(row['product_mrp'],2) if row['product_mrp'] else 0,
                'actual_price': round(row['actual_price'],2) if row['actual_price'] else 0,
                'price_unit': round(row['price_unit'],2) if row['price_unit'] else 0,
                'create_date':x,
                'order_ref':order_ref,
                'receipt_ref':receipt_ref
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
        pos_config_ids = data['form']['pos_config_ids']
        user_id = data['form']['user_id']
        product_id = data['form']['product_id']

        sale = self.get_data(data)

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        docargs = {
            'doc_ids': self.ids,
            'date_start':date_object_date_start.strftime('%d-%m-%Y'),
            'date_end':date_object_date_end.strftime('%d-%m-%Y'),
            'sale':sale,



        }

        return self.env['report'].render('pos_price_edit_report.pos_price_edit_report_view', docargs)
