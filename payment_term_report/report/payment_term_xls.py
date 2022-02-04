from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _



class payment_term_Xls(ReportXlsx):

    def get_lines(self, data,vendor_id):
        
        lines = []
        res ={}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']


        query = '''
            SELECT date_due,date_invoice,number,amount_total,(amount_total-residual) as paid,residual FROM account_invoice where type ='in_invoice'
             AND partner_id = %s and date_due BETWEEN %s and %s AND company_id = %s AND state ='open'
                      
            ORDER BY  date_due ASC
        '''
        self.env.cr.execute(query, (vendor_id,date_start,date_end, company_id,))
        for row in self.env.cr.dictfetchall():
            res = {
                'due_date': row['date_due'],
                'number': row['number'],
                'invoice_date': row['date_invoice'],
                'total_amount': row['amount_total'],
                'paid': row['paid'],
                'balance': row['residual'],

            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    def get_payment(self, data):

        lines = []
        res = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']


        query = '''
           SELECT date_due,date_invoice,number,rp.name,rp.phone,rp.mobile,amount_total,(amount_total-residual) as paid,residual FROM account_invoice as ai
            left join res_partner as rp on rp.id = ai.partner_id where ai.type ='in_invoice' AND ai.state ='open'
             AND  date_due BETWEEN %s and %s AND ai.company_id = %s 
                      
            ORDER BY  date_due ASC
        '''
        self.env.cr.execute(query, (date_start,date_end, company_id,))
        for row in self.env.cr.dictfetchall():
            phone = row['mobile'] if row['mobile'] else row['phone']
            res = {

                'name':row['name'],
                'phone': phone if phone else '',
                'due_date': row['date_due'],
                'number': row['number'],
                'invoice_date': row['date_invoice'],
                'total_amount': row['amount_total'],
                'paid': row['paid'],
                'balance': row['residual'],

            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []


     
    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Payment Term Report'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        
        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 35)
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
        sheet.set_column(17,17, 20)
        sheet.set_column(18, 18, 20)
        sheet.set_column(19, 19, 20)
        sheet.set_column(20, 20, 20)
        
        date_start = data['form']['date_start']
        
        date_end = data['form']['date_end']
        vendor_ids = data['form']['vendor_ids']
        
        
        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})
        
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})
        
        format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right','bold': True})
       
        yellow_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'bold': True,
                                        'bg_color': 'fcf22f'})
        orange_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'bold': True,
                                        'bg_color': 'f4a442'})
        green_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'bold': True,
                                        'bg_color': '32CD32'})
        blue_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'bold': True,
                                        'color':'ffffff','bg_color': '483D8B'})
        blue_mark1 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'bold': True,
                                        'color':'000000','bg_color': '93cddd','align': 'center'})
        blue_mark2 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'bold': True,
                                        'color':'000000','bg_color': 'bdb3ca'})
          
        bold = workbook.add_format({'bold': True})
        
        title_style = workbook.add_format({'font_size': 14,'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})
        
        company = self.env['res.company'].browse(data['form']['company_id']).name
        street = self.env['res.company'].browse(data['form']['company_id']).street

        if vendor_ids:
            sheet.merge_range('A1:F1', company, blue_mark1)
            sheet.merge_range('A2:F2', street, blue_mark1)
            sheet.merge_range('A3:F3', "Payment Term Report", blue_mark1)
            sheet.merge_range('A4:F4', date_start + '-' + date_end, blue_mark1)
            line_row = 5
            line_column = 0
            for vendor_id in vendor_ids:
                calc_line = 0
                partner = self.env['res.partner'].browse(vendor_id)
                for cus in partner:
                    if self.get_lines(data,vendor_id):
                        sheet.write(line_row, line_column, cus.name, font_size_8)
                        if cus.mobile:
                            mobile = cus.mobile
                        else:
                            mobile = cus.phone
                        sheet.write(line_row + 1, line_column, mobile if mobile else " ", font_size_8)
                        sheet.write(line_row + 2, line_column, "Due Date", blue_mark)
                        sheet.write(line_row + 2, line_column + 1, "Invoice Date", blue_mark)
                        sheet.write(line_row + 2, line_column + 2, "Bill", blue_mark)
                        sheet.write(line_row + 2, line_column + 3, "Total Amount", blue_mark)
                        sheet.write(line_row + 2, line_column + 4, "Paid Amount", blue_mark)
                        sheet.write(line_row + 2, line_column + 5, "Balance", blue_mark)
                        line_row = line_row + 3
                        line_column = 0
                        for line in self.get_lines(data,vendor_id):
                            if calc_line == 0 :
                                calc_line = line_row
                            sheet.write(line_row, line_column, line['due_date'], font_size_8)
                            sheet.write(line_row, line_column + 1, line['invoice_date'], font_size_8)
                            sheet.write(line_row, line_column + 2, line['number'], font_size_8)
                            sheet.write(line_row, line_column + 3, line['total_amount'], font_size_8)
                            sheet.write(line_row, line_column + 4, line['paid'], font_size_8)
                            sheet.write(line_row, line_column + 5, line['balance'], font_size_8)
                            line_row = line_row + 1
                            line_column = 0
                        sheet.merge_range(line_row, line_column, line_row, 2, 'Total', font_size_8)
                        total_cell_range = xl_range(calc_line, 3, line_row - 1, 3)
                        total_cell_range2 = xl_range(calc_line, 4, line_row - 1, 4)
                        total_cell_range3 = xl_range(calc_line, 5, line_row - 1, 5)

                        sheet.write_formula(line_row, line_column + 3, '=SUM(' + total_cell_range + ')', orange_mark)
                        sheet.write_formula(line_row, line_column + 4, '=SUM(' + total_cell_range2 + ')', orange_mark)
                        sheet.write_formula(line_row, line_column + 5, '=SUM(' + total_cell_range3 + ')', orange_mark)
                        line_row = line_row + 3
                        line_column = 0
                        calc_line = 0

        else:
            sheet.merge_range('A1:H1', company, blue_mark1)
            sheet.merge_range('A2:H2', street, blue_mark1)
            sheet.merge_range('A3:H3', "Payment Term Report", blue_mark1)
            sheet.merge_range('A4:H4', date_start + '-' + date_end, blue_mark1)
            line_row = 5
            line_column = 0
            sheet.write(line_row, line_column, "Due Date", blue_mark)
            sheet.write(line_row, line_column + 1, "Invoice Date", blue_mark)
            sheet.write(line_row, line_column + 2, "Bill", blue_mark)
            sheet.write(line_row, line_column + 3, "Vendor", blue_mark)
            sheet.write(line_row, line_column + 4, "Phone", blue_mark)
            sheet.write(line_row, line_column + 5, "Total Amount", blue_mark)
            sheet.write(line_row, line_column + 6, "Paid Amount", blue_mark)
            sheet.write(line_row, line_column + 7, "Balance", blue_mark)
            line_row = line_row + 1
            line_column = 0
            for line in self.get_payment(data):
                sheet.write(line_row, line_column, line['due_date'], font_size_8)
                sheet.write(line_row, line_column + 1, line['invoice_date'], font_size_8)
                sheet.write(line_row, line_column + 2, line['number'], font_size_8)
                sheet.write(line_row, line_column + 3, line['name'], font_size_8)
                sheet.write(line_row, line_column + 4, line['phone'], font_size_8)
                sheet.write(line_row, line_column + 5, line['total_amount'], font_size_8)
                sheet.write(line_row, line_column + 6, line['paid'], font_size_8)
                sheet.write(line_row, line_column + 7, line['balance'], font_size_8)

                line_row = line_row + 1
                line_column = 0
            sheet.merge_range(line_row, line_column, line_row, 4,'Total', font_size_8)
            total_cell_range = xl_range(6, 5, line_row - 1, 5)
            total_cell_range2 = xl_range(6, 6, line_row - 1, 6)
            total_cell_range3 = xl_range(6, 7, line_row - 1, 7)

            sheet.write_formula(line_row, line_column + 5, '=SUM(' + total_cell_range + ')', orange_mark)
            sheet.write_formula(line_row, line_column + 6, '=SUM(' + total_cell_range2 + ')', orange_mark)
            sheet.write_formula(line_row, line_column + 7, '=SUM(' + total_cell_range3 + ')', orange_mark)


payment_term_Xls('report.payment_term_report.payment_term_xls.xlsx', 'account.move')
