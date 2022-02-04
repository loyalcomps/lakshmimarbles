# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Inventoryreport(models.AbstractModel):

    _name = 'report.inventory_adjustment_report.inv_report_pdf'

    def get_product(self, data):

        lines = []
        invoice_id = []
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']
        category_id = data['form']['category_id']
        category_only = data['form']['category_only']
        product_id = data['form']['product_id']

        cr = 0

        if product_id != False and category_id == False:

            query22 = '''
                             select (p.barcode) as barcode,
                	(stl.product_name) as pname,
                	(stl.theoretical_qty) as system_qty,
                	(stl.theoretical_qty*stl.cost_price_val) as current_value,
                	(stl.product_qty) as real_value ,
                	((stl.product_qty-stl.theoretical_qty)) as variation,
                	 COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))  as negative_val,
                	COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))  as positive_val,

                	(COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))+
                	 COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))+(stl.theoretical_qty*stl.cost_price_val)) as toatl
               from stock_inventory as st 
                	left join stock_inventory_line as stl on stl.inventory_id=st.id
                	left join product_product as p on p.id=stl.product_id
                	left join product_template as pt on pt.id=p.product_tmpl_id WHERE stl.id in 
         ( SELECT max(stl.id)  FROM  stock_inventory as st 
                	left join stock_inventory_line as stl on stl.inventory_id=st.id
        		left join product_product as s on s.id=stl.product_id
        		 where to_char(date_trunc('day',st.date),'YYYY-MM-DD')
                         ::date = %s and stl.location_id=%s 
                            			 and stl.product_id=%s and st.state in ('done') group by stl.product_id)
                            			  order by pname


                            '''

            self.env.cr.execute(query22, (date_start, stock_location, product_id))
            for row in self.env.cr.dictfetchall():
                # sl = sl + 1

                sale = 0
                possale = 0
                purtotal = 0

                # poscost = row['poscost'] if row['poscost'] else 0
                barcode = row['barcode'] if row['barcode'] else 0
                pname = row['pname'] if row['pname'] else 0

                system_qty = row['system_qty'] if row['system_qty'] else 0
                current_value = row['current_value'] if row['current_value'] else 0
                real_value = row['real_value'] if row['real_value'] else 0
                variation = row['variation'] if row['variation'] else 0
                negative_val = row['negative_val'] if row['negative_val'] else 0
                positive_val = row['positive_val'] if row['positive_val'] else 0
                toatl = row['toatl'] if row['toatl'] else 0

                res = {
                    'barcode': barcode,
                    'pname': pname,
                    'system_qty': system_qty,
                    'current_value': current_value,
                    'real_value': real_value,
                    'variation': variation,
                    'negative_val': negative_val,
                    'positive_val': positive_val,
                    'toatl': toatl,

                }
                lines.append(res)

            if lines:
                return lines
            else:
                return []

    def get_cat_false(self, data):

        lines = []
        invoice_id = []
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']
        category_id = data['form']['category_id']
        category_only = data['form']['category_only']
        product_id = data['form']['product_id']

        cr = 0

        if product_id == False and category_id == False:

            query22 = '''
                             select (p.barcode) as barcode,
                	(stl.product_name) as pname,
                	(stl.theoretical_qty) as system_qty,
                	(stl.theoretical_qty*stl.cost_price_val) as current_value,
                	(stl.product_qty) as real_value ,
                	((stl.product_qty-stl.theoretical_qty)) as variation,
                	 COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))  as negative_val,
                	COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))  as positive_val,

                	(COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))+
                	 COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))+(stl.theoretical_qty*stl.cost_price_val)) as toatl
               from stock_inventory as st 
                	left join stock_inventory_line as stl on stl.inventory_id=st.id
                	left join product_product as p on p.id=stl.product_id
                	left join product_template as pt on pt.id=p.product_tmpl_id WHERE stl.id in 
         ( SELECT max(stl.id)  FROM  stock_inventory as st 
                	left join stock_inventory_line as stl on stl.inventory_id=st.id
        		left join product_product as s on s.id=stl.product_id
        		 where to_char(date_trunc('day',st.date),'YYYY-MM-DD')
                         ::date = %s and stl.location_id=%s and st.state in ('done') group by stl.product_id)
                            			  order by pname


                            '''
            #
            #    if category_only == False:
            #
            #        query21 = '''
            #       select p.barcode as barcode,
            # stl.product_name as pname,
            # stl.theoretical_qty as system_qty,
            # stl.theoretical_qty*stl.cost_price_val as current_value,
            # stl.product_qty as real_value ,
            # (stl.product_qty-stl.theoretical_qty) as variation,
            #  COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ),0)  as negative_val,
            # COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ),0)  as positive_val,
            #
            # COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ),0)+
            #  COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ),0) as toatl,
            #
            # stl.cost_price_val from stock_inventory as st
            # left join stock_inventory_line as stl on stl.inventory_id=st.id
            # left join product_product as p on p.id=stl.product_id
            # left join product_template as pt on pt.id=p.product_tmpl_id
            #
            # where to_char(date_trunc('day',st.date),'YYYY-MM-DD')
            #        			 ::date = %s and stl.location_id=%s and pt.categ_id=%s
            #                                                                                       '''

            self.env.cr.execute(query22, (date_start, stock_location))
            for row in self.env.cr.dictfetchall():
                # sl = sl + 1

                sale = 0
                possale = 0
                purtotal = 0

                # poscost = row['poscost'] if row['poscost'] else 0
                barcode = row['barcode'] if row['barcode'] else 0
                pname = row['pname'] if row['pname'] else 0

                system_qty = row['system_qty'] if row['system_qty'] else 0
                current_value = row['current_value'] if row['current_value'] else 0
                real_value = row['real_value'] if row['real_value'] else 0
                variation = row['variation'] if row['variation'] else 0
                negative_val = row['negative_val'] if row['negative_val'] else 0
                positive_val = row['positive_val'] if row['positive_val'] else 0
                toatl = row['toatl'] if row['toatl'] else 0

                res = {
                    'barcode': barcode,
                    'pname': pname,
                    'system_qty': system_qty,
                    'current_value': current_value,
                    'real_value': real_value,
                    'variation': variation,
                    'negative_val': negative_val,
                    'positive_val': positive_val,
                    'toatl': toatl,

                }
                lines.append(res)

            if lines:
                return lines
            else:
                return []

    def get_line(self, data):

        lines = []
        invoice_id = []
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']
        category_id = data['form']['category_id']
        category_only = data['form']['category_only']
        product_id = data['form']['product_id']

        cr = 0

        if product_id != False and category_id != False:

            query22 = '''
                         select (p.barcode) as barcode,
            	(stl.product_name) as pname,
            	(stl.theoretical_qty) as system_qty,
            	(stl.theoretical_qty*stl.cost_price_val) as current_value,
            	(stl.product_qty) as real_value ,
            	((stl.product_qty-stl.theoretical_qty)) as variation,
            	 COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))  as negative_val,
            	COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))  as positive_val,

            	(COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))+
            	 COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))+(stl.theoretical_qty*stl.cost_price_val)) as toatl
           from stock_inventory as st 
            	left join stock_inventory_line as stl on stl.inventory_id=st.id
            	left join product_product as p on p.id=stl.product_id
            	left join product_template as pt on pt.id=p.product_tmpl_id WHERE stl.id in 
     ( SELECT max(stl.id)  FROM  stock_inventory as st 
            	left join stock_inventory_line as stl on stl.inventory_id=st.id
    		left join product_product as s on s.id=stl.product_id
    		 where to_char(date_trunc('day',st.date),'YYYY-MM-DD')
                     ::date = %s and stl.location_id=%s and pt.categ_id =%s 
                        			 and stl.product_id=%s and st.state in ('done') group by stl.product_id)
                        			  order by pname


                        '''
            #
            #    if category_only == False:
            #
            #        query21 = '''
            #       select p.barcode as barcode,
            # stl.product_name as pname,
            # stl.theoretical_qty as system_qty,
            # stl.theoretical_qty*stl.cost_price_val as current_value,
            # stl.product_qty as real_value ,
            # (stl.product_qty-stl.theoretical_qty) as variation,
            #  COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ),0)  as negative_val,
            # COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ),0)  as positive_val,
            #
            # COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ),0)+
            #  COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ),0) as toatl,
            #
            # stl.cost_price_val from stock_inventory as st
            # left join stock_inventory_line as stl on stl.inventory_id=st.id
            # left join product_product as p on p.id=stl.product_id
            # left join product_template as pt on pt.id=p.product_tmpl_id
            #
            # where to_char(date_trunc('day',st.date),'YYYY-MM-DD')
            #        			 ::date = %s and stl.location_id=%s and pt.categ_id=%s
            #                                                                                       '''

            self.env.cr.execute(query22, (date_start, stock_location, category_id, product_id))
            for row in self.env.cr.dictfetchall():
                # sl = sl + 1

                sale = 0
                possale = 0
                purtotal = 0

                # poscost = row['poscost'] if row['poscost'] else 0
                barcode = row['barcode'] if row['barcode'] else 0
                pname = row['pname'] if row['pname'] else 0

                system_qty = row['system_qty'] if row['system_qty'] else 0
                current_value = row['current_value'] if row['current_value'] else 0
                real_value = row['real_value'] if row['real_value'] else 0
                variation = row['variation'] if row['variation'] else 0
                negative_val = row['negative_val'] if row['negative_val'] else 0
                positive_val = row['positive_val'] if row['positive_val'] else 0
                toatl = row['toatl'] if row['toatl'] else 0

                res = {
                    'barcode': barcode,
                    'pname': pname,
                    'system_qty': system_qty,
                    'current_value': current_value,
                    'real_value': real_value,
                    'variation': variation,
                    'negative_val': negative_val,
                    'positive_val': positive_val,
                    'toatl': toatl,

                }
                lines.append(res)

            if lines:
                return lines
            else:
                return []

    def get_cash(self, data):

        lines = []
        invoice_id = []
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']

        stock_location = data['form']['stock_location']
        category_id = data['form']['category_id']
        category_only = data['form']['category_only']
        product_id = data['form']['product_id']

        cr = 0

        if product_id == False and category_id != False:

            query21 = '''
                    select (p.barcode) as barcode,
            	(stl.product_name) as pname,
            	(stl.theoretical_qty) as system_qty,
            	(stl.theoretical_qty*stl.cost_price_val) as current_value,
            	(stl.product_qty) as real_value ,
            	((stl.product_qty-stl.theoretical_qty)) as variation,
            	 COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))  as negative_val,
            	COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))  as positive_val,

            	(COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)>0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))+
            	 COALESCE((CASE WHEN (stl.product_qty-stl.theoretical_qty)<0 THEN (stl.product_qty-stl.theoretical_qty)*stl.cost_price_val ELSE 0 END ))+(stl.theoretical_qty*stl.cost_price_val)) as toatl
           from stock_inventory as st 
            	left join stock_inventory_line as stl on stl.inventory_id=st.id
            	left join product_product as p on p.id=stl.product_id
            	left join product_template as pt on pt.id=p.product_tmpl_id WHERE stl.id in 
     ( SELECT max(stl.id)  FROM  stock_inventory as st 
            	left join stock_inventory_line as stl on stl.inventory_id=st.id
    		left join product_product as s on s.id=stl.product_id
    		 where to_char(date_trunc('day',st.date),'YYYY-MM-DD')
                     ::date = %s and stl.location_id=%s and pt.categ_id =%s 
                        			 and st.state in ('done') group by stl.product_id) order by pname
                                                    '''

            self.env.cr.execute(query21, (date_start, stock_location, category_id))
            for row in self.env.cr.dictfetchall():
                # sl = sl + 1

                sale = 0
                possale = 0
                purtotal = 0

                # poscost = row['poscost'] if row['poscost'] else 0
                barcode = row['barcode'] if row['barcode'] else 0
                pname = row['pname'] if row['pname'] else 0

                system_qty = row['system_qty'] if row['system_qty'] else 0
                current_value = row['current_value'] if row['current_value'] else 0
                real_value = row['real_value'] if row['real_value'] else 0
                variation = row['variation'] if row['variation'] else 0
                negative_val = row['negative_val'] if row['negative_val'] else 0
                positive_val = row['positive_val'] if row['positive_val'] else 0
                toatl = row['toatl'] if row['toatl'] else 0

                res = {
                    'barcode': barcode,
                    'pname': pname,
                    'system_qty': system_qty,
                    'current_value': current_value,
                    'real_value': real_value,
                    'variation': variation,
                    'negative_val': negative_val,
                    'positive_val': positive_val,
                    'toatl': toatl,

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

        stock_location = data['form']['stock_location']
        category_id = data['form']['category_id']
        category_only = data['form']['category_only']
        product_id = data['form']['product_id']

        stock_location = data['form']['stock_location']
        stock_parent = self.env["stock.location"].browse(stock_location).location_id.name
        stock_name = self.env["stock.location"].browse(stock_location).name
        category_name =self.env["product.category"].browse(category_id).name



        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()


        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        valueone = self.get_cash(data)
        valuetwo =self.get_line(data)
        valuethree= self.get_cat_false(data)
        valuefour=self.get_product(data)

        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date_start.strftime('%d-%m-%Y'),
            'data': data['form'],
            'time': time,
            'category_name':category_name,
            # 'name_de':name_de,
            'data': data['form'],
            'doc_ids': self.ids,
            'data': data['form'],
            'doc_ids': self.ids,
            'valueone':valueone if valueone else 0,
            'stock_location': stock_name,
            'stock_name': stock_parent,
            'cat_only': category_only,
            'valuetwo':valuetwo if valuetwo else 0,
            'category_id':category_id,
            'product_id':product_id,
            'valuethree':valuethree,
            'valuefour':valuefour,




            'time': time,


        }

        return self.env['report'].render('inventory_adjustment_report.inv_report_pdf', docargs)
