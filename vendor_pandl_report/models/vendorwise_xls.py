from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from odoo.tools.translate import _


class VendorWise(ReportXlsx):

    def get_vendor_wise(self, data,vendor_id):
        lines = []
        product=[]

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        product_ids = data['form']['product_id']


        if product_ids:
            invoice_ids = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start),
                 ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id), ('partner_id', '=', vendor_id),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid']),
                 ('product_id','in',product_ids)])
        else:
            invoice_ids = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start),
                 ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),('partner_id', '=', vendor_id),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])
        for invoice in invoice_ids:
            product_id = self.env['product.product'].search([('id','=',invoice.product_id.id)]).id
            if product_id not in product:
                product.append(product_id)


        sl=0
        for i in product:
            p_qty = 0
            p_amt = 0
            sl += 1
            for k in invoice_ids:
                if i == k.product_id.id:
                    p_amt += k.price_subtotal_taxinc
                    p_qty += k.quantity
            product_obj = self.env['product.product'].browse(i)
            for obj in product_obj:
                product_name = obj.name
                qty_onhand = obj.qty_available
                cost = obj.standard_price
                landing_cost = obj.landing_cost
            res = {
                'sl_no': sl,
                'product': product_name,
                'onhand':qty_onhand,
                'cost': cost,
                'landing_cost':landing_cost,
                'p_qty': p_qty,
                'purchase': p_amt,
            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_vendor_contact_wise(self, data,vendor_id):
        lines = []
        product=[]

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        product_id = data['form']['product_id']

        if product_id:
            invoice_ids = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start),
                 ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id), ('partner_id', '=', vendor_id),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid']),
                 ('product_id','in',product_id)])
        else:
            invoice_ids = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start),
                 ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),('partner_id', '=', vendor_id),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])
        for invoice in invoice_ids:
            product_id = self.env['product.product'].search([('id','=',invoice.product_id.id)]).id
            if product_id not in product:
                product.append(product_id)

        sl=0
        for i in product:
            p_qty = 0
            p_amt = 0
            sl += 1
            for k in invoice_ids:
                if i == k.product_id.id:
                    p_amt += k.price_subtotal_taxinc
                    p_qty += k.quantity
            product_obj = self.env['product.product'].browse(i)
            for obj in product_obj:
                product_name = obj.name
                qty_onhand = obj.qty_available
                cost = obj.standard_price
                landing_cost = obj.landing_cost

            res = {
                'sl_no': sl,
                'product': product_name,
                'cost': cost,
                'onhand':qty_onhand,
                'landing_cost': landing_cost,
                'p_qty': p_qty,
                'purchase': p_amt,

            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def get_product_sale_info(self, data):
        lines = []
        product=[]


        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        product_ids = data['form']['product_id']
        vendor_ids = data['form']['vendor_id']
        vendor_contact_ids = data['form']['vendor_contact_id']
        vendor_list = vendor_ids+vendor_contact_ids


        if product_ids:
            product = product_ids
        else:
 #            query ='''
 #             select distinct(ai.product_id) from account_invoice_line as ai
 # left join account_invoice as a on a.id=ai.invoice_id
 # where a.type='in_invoice' and a.state in ('open','paid') and a.company_id = %s and a.partner_id in (163)
 # and  to_char(date_trunc('day',a.date_invoice),'YYYY-MM-DD')::date between %s and %s
 #            '''
 #            self.env.cr.execute(query, (company_id,date_start,date_end))
 #            for row in self.env.cr.dictfetchall():
 #                product.append(row['product_id'])
            invoice_ids = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start),
                 ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),('partner_id', 'in', vendor_list),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])
            for invoice in invoice_ids:
                product_id = self.env['product.product'].search([('id','=',invoice.product_id.id)]).id
                if product_id not in product:
                    product.append(product_id)

        if product:
            out_invoice_lines = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id), ('invoice_id.type', '=', 'out_invoice'),('invoice_id.state', 'in', ['open', 'paid']),
                 ('product_id', 'in', product)])
        sl=0
        for i in product:
            s_amt = 0
            s_qty = 0
            sl += 1
            for l in out_invoice_lines:
                if i == l.product_id.id:
                    s_amt += l.price_subtotal_taxinc
                    s_qty += l.quantity
            product_name = self.env['product.product'].search([('id','=',i)]).name
            average_sale_price = (s_amt/s_qty)if s_qty !=0 else 0
            res = {
                'sl_no': sl,
                'product': product_name,
                'average_sale_price':average_sale_price,
                's_qty': s_qty,
                'sale': s_amt,
            }
            if res['s_qty']:
                lines.append(res)

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Vendor wise P&L Report'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 0, 25)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 10)
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

        date_start = data['form']['date_start']

        date_end = data['form']['date_end']
        vendor_id = data['form']['vendor_id']
        vendor_contact_id = data['form']['vendor_contact_id']
        product_id = data['form']['product_id']

        # vendor_name = self.env["res.partner"].browse(vendor_id).name

        company = self.env['res.company'].browse(data['form']['company_id']).name

        company_address = self.env['res.company'].browse(data['form']['company_id']).street


        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right', 'bold': True,})

        format11 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center', 'bold': True})
        yellow_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': 'fcf22f','align': 'center'})

        orange_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': 'f4a442'})

        green_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'bg_color': '32CD32'})

        blue_mark = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': 'ffffff', 'bg_color': '483D8B'})

        bold = workbook.add_format({'bold': True})

        title_style = workbook.add_format({'font_size': 14, 'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        sheet.merge_range('C1:E1', company, format11)
        sheet.merge_range('C2:E2', company_address, format11)
        sheet.merge_range('C3:E3', "Vendor Wise Profit and Loss Report ", format11)
        sheet.merge_range('C4:E4', date_start + '-' + date_end,format11)

        line_row = 6
        line_column = 0
        for vendor in vendor_id:
            value =self.get_vendor_wise(data,vendor)
            if value:
                vendor_name = self.env["res.partner"].browse(vendor).name
                cell1 = xl_rowcol_to_cell(line_row, 0)
                cell2 = xl_rowcol_to_cell(line_row, 6)
                sheet.merge_range(cell1 + ':' + cell2, "VENDOR :- " + vendor_name, yellow_mark)
                # sheet.write(line_row, line_column, "VENDOR:-", yellow_mark)
                # sheet.write(line_row, line_column+1, vendor_name, yellow_mark)
                line_row += 1
                line_column = 0
                sheet.write(line_row, line_column, "Sl No", blue_mark)
                sheet.write(line_row, line_column+1, "Product", blue_mark)
                sheet.write(line_row, line_column+2, "Onhand", blue_mark)
                sheet.write(line_row, line_column+3, "Cost", blue_mark)
                sheet.write(line_row, line_column+4, "Landing Cost", blue_mark)
                sheet.write(line_row, line_column+5, "Purchased Qty", blue_mark)
                sheet.write(line_row, line_column+6, "Purchase Amount", blue_mark)

                line_row += 1
                row = line_row
                line_column = 0
                for line in value:
                    sheet.write(line_row, line_column, line['sl_no'], font_size_8)
                    sheet.write(line_row, line_column + 1, line['product'], font_size_8)
                    sheet.write(line_row, line_column + 2, line['onhand'], font_size_8)
                    sheet.write(line_row, line_column + 3, line['cost'], font_size_8)
                    sheet.write(line_row, line_column + 4, line['landing_cost'], font_size_8)
                    sheet.write(line_row, line_column + 5, line['p_qty'], font_size_8)
                    sheet.write(line_row, line_column + 6, line['purchase'], font_size_8)

                    line_row = line_row + 1
                    line_column = 0
                cell1 = xl_rowcol_to_cell(line_row, 0)
                cell2 = xl_rowcol_to_cell(line_row, 4)
                sheet.merge_range(cell1+':'+cell2,"TOTAL", format1)
                # sheet.write(line_row, 0, "TOTAL", format1)
                total_cell_range = xl_range(row, 5, line_row - 1, 5)
                total_cell_range_one = xl_range(row, 6, line_row - 1, 6)
                sheet.write_formula(line_row, 5, '=SUM(' + total_cell_range + ')', format1)
                sheet.write_formula(line_row, 6, '=SUM(' + total_cell_range_one + ')', format1)
                line_row = line_row + 2
                line_column = 0
        for vendor in vendor_contact_id:
            value = self.get_vendor_contact_wise(data,vendor)
            if value:
                vendor_id = self.env["res.partner"].browse(vendor)
                for partner_id in vendor_id:
                    vendor_name = partner_id.parent_id.name+","+partner_id.name
                cell1 = xl_rowcol_to_cell(line_row, 0)
                cell2 = xl_rowcol_to_cell(line_row, 6)
                sheet.merge_range(cell1 + ':' + cell2, "VENDOR :- "+ vendor_name, yellow_mark)
                # sheet.write(line_row, line_column, "VENDOR:-", yellow_mark)
                # sheet.write(line_row, line_column + 1, vendor_name, yellow_mark)
                line_row += 1
                line_column = 0
                sheet.write(line_row, line_column, "Sl No", blue_mark)
                sheet.write(line_row, line_column + 1, "Product", blue_mark)
                sheet.write(line_row, line_column + 2, "Onhand", blue_mark)
                sheet.write(line_row, line_column + 3, "Cost", blue_mark)
                sheet.write(line_row, line_column + 4, "Landing Cost", blue_mark)
                sheet.write(line_row, line_column + 5, "Purchased Qty", blue_mark)
                sheet.write(line_row, line_column + 6, "Purchase Amount", blue_mark)

                line_row += 1
                row = line_row
                line_column = 0
                for line in value:
                    sheet.write(line_row, line_column, line['sl_no'], font_size_8)
                    sheet.write(line_row, line_column + 1, line['product'], font_size_8)
                    sheet.write(line_row, line_column + 2, line['onhand'], font_size_8)
                    sheet.write(line_row, line_column + 3, line['cost'], font_size_8)
                    sheet.write(line_row, line_column + 4, line['landing_cost'], font_size_8)
                    sheet.write(line_row, line_column + 5, line['p_qty'], font_size_8)
                    sheet.write(line_row, line_column + 6, line['purchase'], font_size_8)

                    line_row = line_row + 1
                    line_column = 0
                cell1 = xl_rowcol_to_cell(line_row, 0)
                cell2 = xl_rowcol_to_cell(line_row, 4)
                sheet.merge_range(cell1 + ':' + cell2, "TOTAL", format1)


                total_cell_range = xl_range(row, 5, line_row - 1, 5)
                total_cell_range_one = xl_range(row, 6, line_row - 1, 6)

                sheet.write_formula(line_row, 5, '=SUM(' + total_cell_range + ')', format1)
                sheet.write_formula(line_row, 6, '=SUM(' + total_cell_range_one + ')', format1)
                line_row = line_row + 2
                line_column = 0


        value = self.get_product_sale_info(data)
        if value:
            cell1 = xl_rowcol_to_cell(line_row, 0)
            cell2 = xl_rowcol_to_cell(line_row, 4)
            sheet.merge_range(cell1 + ':' + cell2, "SALE INFO", yellow_mark)
            line_row +=1
            line_column = 0
            sheet.write(line_row, line_column, "Sl No", blue_mark)
            sheet.write(line_row, line_column + 1, "Product", blue_mark)
            sheet.write(line_row, line_column + 2, "Avg. Sale Price", blue_mark)
            sheet.write(line_row, line_column + 3, "Sold Qty", blue_mark)
            sheet.write(line_row, line_column + 4, "Sale Amount", blue_mark)


            line_row += 1
            row = line_row
            line_column = 0
            for line in value:
                sheet.write(line_row, line_column, line['sl_no'], font_size_8)
                sheet.write(line_row, line_column + 1, line['product'], font_size_8)
                sheet.write(line_row, line_column + 2, line['average_sale_price'], font_size_8)
                sheet.write(line_row, line_column + 3, line['s_qty'], font_size_8)
                sheet.write(line_row, line_column + 4, line['sale'], font_size_8)
                line_row = line_row + 1
                line_column = 0
            cell1 = xl_rowcol_to_cell(line_row, 0)
            cell2 = xl_rowcol_to_cell(line_row, 2)
            sheet.merge_range(cell1 + ':' + cell2, "TOTAL", format1)


            total_cell_range11 = xl_range(row, 3, line_row - 1, 3)
            total_cell_range = xl_range(row, 4, line_row - 1, 4)

            sheet.write_formula(line_row, 3, '=SUM(' + total_cell_range11 + ')', format1)
            sheet.write_formula(line_row, 4, '=SUM(' + total_cell_range + ')', format1)



VendorWise('report.vendor_pandl_report.vendorwise_pandl_xls.xlsx', 'sale.order')
