from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _


class Gst_BtoB_Reg_Xls(ReportXlsx):


    def get_opening(self, data):
 
        datas = {}
        data2 = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
# 
        company_id = data['form']['company_id']

        value = 0
        return value
    

    def get_lines(self, data):
        
        lines = []
        res ={}
        val = {}
        inv = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        company_id = data['form']['company_id']

        # current_company_id = data['form']['current_company_id']

        inv_ids = self.env["account.invoice"].search([('date_invoice', '>=', date_start ),
                                                 ('date_invoice', '<=', date_end ),
                                                 ('company_id','=',company_id),
                                                 ('type','=','out_invoice')])
        # state_id=self.env["res.company"].browse(current_company_id)

        tax_ids = self.env["account.tax"].search([])

        # for i in inv_ids:
        #     for j in i.tax_line_ids:
        #         if j.invoice_id.partner_id.state_code != state_id.state_code:
        #
        #             res = {
        #                 'c_name': j.invoice_id.partner_id.name,
        #                 'c_gstin': j.invoice_id.partner_id.gst_in,
        #                 'inv_no': j.invoice_id.move_name,
        #                 'inv_date': j.invoice_id.date_invoice,
        #                 # 'inv_val': j.taxable_value,
        #                 'tax_rate': j.name,
        #                 'tax_val': j.amount,
        #                 'igst': j.amount,
        #                 'cgst': 0,
        #                 'sgst': 0
        #
        #             }
        #         else :
        #             res = {
        #                 'c_name': j.invoice_id.partner_id.name,
        #                 'c_gstin': j.invoice_id.partner_id.gst_in,
        #                 'inv_no': j.invoice_id.move_name,
        #                 'inv_date': j.invoice_id.date_invoice,
        #                 # 'inv_val': j.taxable_value,
        #                 'tax_rate': j.name,
        #                 'tax_val': j.amount,
        #                 'igst': 0,
        #                 'cgst': j.amount/2,
        #                 'sgst': j.amount/2
        #
        #             }
        #
        #         lines.append(res)
        #
        # if lines:
        #     return lines
        # else:
        #     return []

        sl = 0
        # for i in inv_ids:
        #     if not i.id in inv:
        #         inv.append(i.id)

        for j in inv_ids:


            for i in tax_ids:

                inv_line_id = self.env["account.invoice.line"].search([('invoice_line_tax_ids', '=', i.id), ('invoice_id', '=', j.id)])
                for k in inv_line_id:
                    for t in k.invoice_line_tax_ids:
                        if not t.id in inv:
                            inv.append(i.id)

        for j in inv_ids:

            for i in inv:
                total_qty = 0
                total_amt = 0
                total_tax = 0
                igst = 0
                cgst = 0
                sgst = 0
                total = 0

                inv_line_id = self.env["account.invoice.line"].search(
                    [('invoice_line_tax_ids', '=', i), ('invoice_id', '=', j.id)])
                taxname = self.env['account.tax'].browse(i).name
                for k in inv_line_id:
                    total_amt += k.price_subtotal
                    total_tax += k.price_subtotal_taxinc - k.price_subtotal
                    total += k.price_subtotal_taxinc
                    if k.partner_id.state_code != k.company_id.state_code:
                        # (l.price_subtotal * o.amount) / (100 * 2)
                        igst += k.price_subtotal_taxinc - k.price_subtotal
                    else:
                        cgst += (k.price_subtotal_taxinc - k.price_subtotal) / 2
                        sgst += (k.price_subtotal_taxinc - k.price_subtotal) / 2
                sl = sl + 1

                res = {
                    'sl_no':sl,
                    'c_name': j.partner_id.name,
                    'c_gstin': j.partner_id.gst_in,
                    'inv_no': j.move_name,
                    'inv_date': j.date_invoice,
                    'inv_val': total_amt,
                    'tax_rate': taxname,
                    'tax_val': total_tax,
                    'igst': igst,
                    'cgst': cgst,
                    'sgst': sgst,
                    'total':total
                    }
                lines.append(res)

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('B2B'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        
        sheet.set_column(0, 0, 25)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        
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
        sheet.set_column(17,17, 20)
        sheet.set_column(18, 18, 20)
        sheet.set_column(19, 19, 20)
        sheet.set_column(20, 20, 20)
        
        
        date_start = data['form']['date_start']
        
        date_end = data['form']['date_end']
        
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
        
        bold = workbook.add_format({'bold': True})
        
        title_style = workbook.add_format({'font_size': 14,'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        
#         sheet.write('A1'," Report",format1)
        
        sheet.merge_range('A1:B1',"B2B - to registered persons", format1)
        sheet.write('D1',"DATE :-", format1)
        sheet.merge_range('E1:F1',date_start + ' - ' + date_end, format1)

        sheet.write('A3', "Sl No", blue_mark)
        sheet.write('B3',"Customer Name",blue_mark)
        sheet.write('C3',"GSTIN",blue_mark)
        sheet.write('D3',"Invoice No",blue_mark)
        sheet.write('E3',"Invoice Date ",blue_mark)
        sheet.write('F3',"Invoice Value ",blue_mark)
        sheet.write('G3',"Tax Rate",blue_mark)
        sheet.write('H3',"GST Tax Value",blue_mark)
        sheet.write('I3',"IGST",blue_mark)
        sheet.write('J3',"Central Tax ",blue_mark)
        sheet.write('K3',"State Tax ",blue_mark)
        sheet.write('L3', "Total", blue_mark)


        
        
        linw_row =3

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column , line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column+1, line['c_name'], font_size_8)
            sheet.write(linw_row, line_column+2, line['c_gstin'], font_size_8)
            sheet.write(linw_row, line_column+3, line['inv_no'], font_size_8)
            sheet.write(linw_row, line_column+4, line['inv_date'], font_size_8)
            sheet.write_number(linw_row, line_column +5, line['inv_val'], font_size_8)
            sheet.write(linw_row, line_column+6, line['tax_rate'], font_size_8)
            sheet.write_number(linw_row, line_column+7, line['tax_val'], font_size_8)
            sheet.write_number(linw_row, line_column+8, line['igst'], font_size_8)
            sheet.write_number(linw_row, line_column+9, line['cgst'], font_size_8)
            sheet.write_number(linw_row, line_column+10, line['sgst'], font_size_8)
            sheet.write_number(linw_row, line_column + 11, line['total'], font_size_8)
            linw_row = linw_row +1
            line_column=0
     
#   #      sheet.merge_range(linw_row,0,linw_row,2, "TOTAL", format1)

        sheet.write(linw_row,0, "TOTAL", format1)
        total_cell_range11 = xl_range(3, 5, linw_row - 1, 5)
        total_cell_range = xl_range(3,7,linw_row-1, 7)
        total_cell_range_one = xl_range(3, 8, linw_row - 1, 8)
        total_cell_range_two = xl_range(3, 9, linw_row - 1, 9)
        total_cell_range_three = xl_range(3, 10, linw_row - 1, 10)
        total_cell_range_four = xl_range(3, 11, linw_row - 1, 11)

        sheet.write_formula(linw_row, 5, '=SUM(' + total_cell_range11 + ')', format1)
        sheet.write_formula(linw_row, 7, '=SUM('+total_cell_range+')', format1)
        sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range_one + ')', format1)
        sheet.write_formula(linw_row, 9, '=SUM(' + total_cell_range_two + ')', format1)
        sheet.write_formula(linw_row, 10, '=SUM(' + total_cell_range_three + ')', format1)
        sheet.write_formula(linw_row, 11, '=SUM(' + total_cell_range_four + ')', format1)



Gst_BtoB_Reg_Xls('report.gst_btob_reg_xls.income_btob_xls.xlsx', 'account.invoice')
