from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from datetime import datetime


class inventoryreport(ReportXlsx):

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

        if product_id != False and category_id != False :

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

            self.env.cr.execute(query22, (date_start, stock_location, category_id,product_id ))
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

        if product_id==False and category_id != False:

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

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Inventory Report'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 20)
        sheet.set_column(6, 6, 20)
        sheet.set_column(7, 7, 20)
        sheet.set_column(8, 8, 20)
        sheet.set_column(9, 9, 20)
        sheet.set_column(10, 10, 20)
        sheet.set_column(11, 11, 20)
        sheet.set_column(12, 12, 20)
        sheet.set_column(13, 13, 20)
        sheet.set_column(14, 14, 20)
        sheet.set_column(15, 15, 20)
        sheet.set_column(16, 16, 20)
        sheet.set_column(17, 17, 20)
        sheet.set_column(18, 18, 20)
        sheet.set_column(19, 19, 20)
        sheet.set_column(20, 20, 20)


        company_id = data['form']['company_id']
        date_start = data['form']['date_start']
        company_id = data['form']['company_id']
        product_id = data['form']['product_id']

        stock_location = data['form']['stock_location']
        category_id = data['form']['category_id']
        category_only = data['form']['category_only']

        stock_location = data['form']['stock_location']
        stock_parent = self.env["stock.location"].browse(stock_location).location_id.name
        stock_name = self.env["stock.location"].browse(stock_location).name


        # vendor_name = self.env["res.partner"].browse(vendor_id).name

        company = self.env['res.company'].browse(data['form']['company_id']).name
        #
        company_address = self.env['res.company'].browse(data['form']['company_id']).street

        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True})

        format11 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
             'bold': True})
        yellow_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': 'fcf22f'})

        orange_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': 'f4a442'})

        green_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': '32CD32'})

        blue_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': 'ffffff', 'bg_color': '483D8B'})

        blue_mark2 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca', 'align': 'center'})
        blue_mark24 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca', 'align': 'left'})

        blue_mark3 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 18, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca', 'align': 'center'})

        date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        # date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        # if brand_id:

        sheet.merge_range('A1:I1', company, blue_mark3)
        sheet.merge_range('A2:I2', company_address, blue_mark2)
        sheet.merge_range('A3:I3', "Inventory Report ", blue_mark2)
        sheet.merge_range('A4:I4', date_object_date_start.strftime(
            '%d-%m-%Y'), blue_mark2)
        sheet.merge_range('A5:I5', "Location :- "+  stock_parent + stock_name, blue_mark24)

        sheet.write('A7', "Barcode", blue_mark)
        sheet.write('B7', "Product", blue_mark)

        sheet.write('C7', "Current system stock", blue_mark)
        sheet.write('D7', "Current_value", blue_mark)
        sheet.write('E7', "Current Physical stock", blue_mark)
        sheet.write('F7', "variation", blue_mark)
        sheet.write('G7', "Negative value", blue_mark)
        sheet.write('H7', "Positive value", blue_mark)
        sheet.write('I7', "Total", blue_mark)


        linw_row = 7

        line_column = 0


        if product_id != False and category_id == False:

            for line in self.get_product(data):
                sheet.write(linw_row, line_column, line['barcode'], font_size_8)
                sheet.write(linw_row, line_column + 1, line['pname'], font_size_8)
                sheet.write(linw_row, line_column + 2, line['system_qty'], font_size_8)

                sheet.write(linw_row, line_column + 3, line['current_value'], font_size_8)
                sheet.write(linw_row, line_column + 4, line['real_value'], font_size_8)
                sheet.write(linw_row, line_column + 5, line['variation'], font_size_8)
                sheet.write(linw_row, line_column + 6, line['negative_val'], font_size_8)
                sheet.write(linw_row, line_column + 7, line['positive_val'], font_size_8)
                sheet.write(linw_row, line_column + 8, line['toatl'], font_size_8)

                linw_row = linw_row + 1
                line_column = 0

            line_column = 0

            sheet.write(linw_row, 0, "TOTAL", format1)

            total_cell_range14 = xl_range(3, 8, linw_row - 1, 8)

            sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range14 + ')', format1)


        if product_id == False and category_id == False:

            for line in self.get_cat_false(data):
                sheet.write(linw_row, line_column, line['barcode'], font_size_8)
                sheet.write(linw_row, line_column + 1, line['pname'], font_size_8)
                sheet.write(linw_row, line_column + 2, line['system_qty'], font_size_8)

                sheet.write(linw_row, line_column + 3, line['current_value'], font_size_8)
                sheet.write(linw_row, line_column + 4, line['real_value'], font_size_8)
                sheet.write(linw_row, line_column + 5, line['variation'], font_size_8)
                sheet.write(linw_row, line_column + 6, line['negative_val'], font_size_8)
                sheet.write(linw_row, line_column + 7, line['positive_val'], font_size_8)
                sheet.write(linw_row, line_column + 8, line['toatl'], font_size_8)

                linw_row = linw_row + 1
                line_column = 0

            line_column = 0

            sheet.write(linw_row, 0, "TOTAL", format1)

            total_cell_range14 = xl_range(3, 8, linw_row - 1, 8)

            sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range14 + ')', format1)

        if product_id==False and category_id != False:


            for line in self.get_cash(data):
                sheet.write(linw_row, line_column, line['barcode'], font_size_8)
                sheet.write(linw_row, line_column + 1, line['pname'], font_size_8)
                sheet.write(linw_row, line_column + 2, line['system_qty'], font_size_8)

                sheet.write(linw_row, line_column + 3, line['current_value'], font_size_8)
                sheet.write(linw_row, line_column + 4, line['real_value'], font_size_8)
                sheet.write(linw_row, line_column + 5, line['variation'], font_size_8)
                sheet.write(linw_row, line_column + 6, line['negative_val'], font_size_8)
                sheet.write(linw_row, line_column + 7, line['positive_val'], font_size_8)
                sheet.write(linw_row, line_column + 8, line['toatl'], font_size_8)


                linw_row = linw_row + 1
                line_column = 0

            line_column = 0



            sheet.write(linw_row, 0, "TOTAL", format1)

            # total_cell_range12 = xl_range(3, 3, linw_row - 1, 3)
            # total_cell_range11 = xl_range(3, 4, linw_row - 1, 4)
            # total_cell_range = xl_range(3, 5, linw_row - 1, 5)
            # total_cell_range_one = xl_range(3, 6, linw_row - 1, 6)
            #
            # total_cell_range13 = xl_range(3, 7, linw_row - 1, 7)
            total_cell_range14 = xl_range(3, 8, linw_row - 1, 8)
            # total_cell_range15 = xl_range(3, 9, linw_row - 1, 9)
            # total_cell_range16 = xl_range(3, 10, linw_row - 1, 10)
            #
            # total_cell_range17 = xl_range(3, 11, linw_row - 1, 11)
            # total_cell_range18 = xl_range(3, 12, linw_row - 1, 12)
            # total_cell_range19 = xl_range(3, 13, linw_row - 1, 13)
            # total_cell_range21 = xl_range(3, 14, linw_row - 1, 14)
            # total_cell_range22 = xl_range(3, 15, linw_row - 1, 15)
            # total_cell_range20 = xl_range(3, 2, linw_row - 1, 2)
            # total_cell_range25 = xl_range(3, 1, linw_row - 1, 1)
            # total_cell_range_three = xl_range(3, 6, linw_row - 1, 6)

            # sheet.write_formula(linw_row, 3, '=SUM(' + total_cell_range12 + ')', format1)
            # sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range11 + ')', format1)
            # sheet.write_formula(linw_row, 5, '=SUM(' + total_cell_range + ')', format1)
            # sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_one + ')', format1)
            #
            # sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range13 + ')', format1)
            sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range14 + ')', format1)

            # sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_three + ')', format1)

        if product_id != False and category_id != False :


            for line in self.get_line(data):
                sheet.write(linw_row, line_column, line['barcode'], font_size_8)
                sheet.write(linw_row, line_column + 1, line['pname'], font_size_8)
                sheet.write(linw_row, line_column + 2, line['system_qty'], font_size_8)

                sheet.write(linw_row, line_column + 3, line['current_value'], font_size_8)
                sheet.write(linw_row, line_column + 4, line['real_value'], font_size_8)
                sheet.write(linw_row, line_column + 5, line['variation'], font_size_8)
                sheet.write(linw_row, line_column + 6, line['negative_val'], font_size_8)
                sheet.write(linw_row, line_column + 7, line['positive_val'], font_size_8)
                sheet.write(linw_row, line_column + 8, line['toatl'], font_size_8)


                linw_row = linw_row + 1
                line_column = 0

            line_column = 0



            sheet.write(linw_row, 0, "TOTAL", format1)

            total_cell_range14 = xl_range(3, 8, linw_row - 1, 8)


            sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range14 + ')', format1)



inventoryreport('report.inventory_adjustment_report.inventory_report_xls.xlsx', 'sale.order')
