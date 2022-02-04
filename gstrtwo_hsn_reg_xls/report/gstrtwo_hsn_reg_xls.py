from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _


class GstTwo_HSN_Reg_Xls(ReportXlsx):

    def get_opening(self, data):
 
        datas = {}
        data2 = {}
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']

        value = 0
        return value
    

    def get_lines(self, data):
        
        lines = []
        res ={}
        hsn=[]
        
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        company = self.env['res.company'].browse(data['form']['company_id']).name
        pdt_ids = self.env["product.product"].search([])
        inv_ids = self.env["account.invoice"].search([('date_invoice', '>=', date_start ),
                                                 ('date_invoice', '<=', date_end ),
                                                 ('company_id','=',company_id),
                                                 ('type','=','in_invoice')])






        # for j in inv_ids:
        #     for i in j.gst_tax_ids:
        #         if not i.hsn in hsn:
        #             hsn.append(i.hsn)
        #
        #
        # for i in hsn:
        #     for j in inv_ids:
        #         for k in j.gst_tax_ids:
        #             res = {
        #                 'c_hsn': i,
        #                 'c_uom': i,
        #                 'tot_qty': i,
        #                 'tot_val': k.taxable_value,
        #                 'tot_tax': i,
        #                 'igst': k.integrated_amount,
        #                 'cgst': k.central_amount,
        #                 'sgst': k.state_amount
        #             }
        #             lines.append(res)
        #
        #
        #
        # if lines:
        #     return lines
        # else:
        #     return []


        sl = 0
        for i in pdt_ids:
            if not i.hsn in hsn:
                 hsn.append(i.hsn)

        for i in hsn:

            total_qty=0
            total_amt = 0
            total_tax = 0
            igst =0
            cgst =0
            sgst =0
            total=0

            for j in inv_ids:
                inv_line_id=self.env["account.invoice.line"].search([('product_id.hsn', '=',i),('invoice_id', '=',j.id)])
                for k in inv_line_id:
                    total_qty += k.quantity
                    total_amt += k.price_subtotal
                    total_tax += k.price_subtotal_taxinc - k.price_subtotal
                    total += k.price_subtotal_taxinc
                    if k.partner_id.state_code != k.company_id.state_code:
                        igst += k.price_subtotal_taxinc - k.price_subtotal
                    else:
                        cgst +=(k.price_subtotal_taxinc -k.price_subtotal)/2
                        sgst += (k.price_subtotal_taxinc - k.price_subtotal)/2
            sl = sl + 1
            res = {
                    'sl_no': sl,
                    'c_hsn': i,
                    'c_uom': i,
                    'tot_qty': total_qty,
                    'tot_val': total_amt,
                    'tot_tax': total_tax,
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
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 25)
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
        sheet.set_column(17,17, 20)
        sheet.set_column(18, 18, 20)
        sheet.set_column(19, 19, 20)
        sheet.set_column(20, 20, 20)
        
        
        date_start = data['form']['date_start']
        
        date_end = data['form']['date_end']
        
        company = self.env['res.company'].browse(data['form']['company_id']).name
        
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


        sheet.merge_range('A1:B1',"GSTR2 HSN Report", format1)
        sheet.merge_range('C1:D1',company, format1)
        sheet.write('E1',"DATE :-", format1)
        sheet.merge_range('F1:G1',date_start + ' - ' + date_end, format1)
        

        sheet.write('A4'," SL No",blue_mark)
        sheet.write('B4',"HSN/SAC",blue_mark)
        sheet.write('C4',"Unit of measurement",blue_mark)
        sheet.write('D4',"Total Quantity ",blue_mark)
        sheet.write('E4',"Total Taxable",blue_mark)
        sheet.write('F4',"GST Amount",blue_mark)
        sheet.write('G4',"IGST ",blue_mark)
        sheet.write('H4',"Central Tax ",blue_mark)
        sheet.write('I4',"State Tax ",blue_mark)
        sheet.write('J4',"Amount ",blue_mark)

        
        
        linw_row =4

        line_column = 0

        for line in self.get_lines(data):
            
            sheet.write(linw_row, line_column, line['sl_no'], font_size_8)
            sheet.write(linw_row, line_column+1, line['c_hsn'], font_size_8)
            sheet.write(linw_row, line_column+2, line['c_uom'], font_size_8)
            sheet.write(linw_row, line_column+3, line['tot_qty'], font_size_8)
            sheet.write_number(linw_row, line_column+4, line['tot_val'], font_size_8)
            sheet.write_number(linw_row, line_column+5, line['tot_tax'], font_size_8)
            sheet.write_number(linw_row, line_column+6, line['igst'], font_size_8)
            sheet.write_number(linw_row, line_column+7, line['cgst'], font_size_8)
            sheet.write_number(linw_row, line_column+8, line['sgst'], font_size_8)
            sheet.write_number(linw_row, line_column+9, line['total'], font_size_8)

            linw_row = linw_row +1
            line_column=0

        total_cell_range = xl_range(4,5,linw_row-1, 5)
        total_cell_range_one = xl_range(4, 9, linw_row - 1, 9)
        total_cell_range_two = xl_range(4, 8, linw_row - 1, 8)
        total_cell_range_three = xl_range(4, 7, linw_row - 1, 7)
        total_cell_range_four = xl_range(4, 6, linw_row - 1, 6)
        total_cell_range_five = xl_range(4, 4, linw_row - 1, 4)

        sheet.write_formula(linw_row, 5, '=SUM('+total_cell_range+')', format1)
        sheet.write_formula(linw_row, 9, '=SUM(' + total_cell_range_one + ')', format1)
        sheet.write_formula(linw_row, 8, '=SUM(' + total_cell_range_two + ')', format1)
        sheet.write_formula(linw_row, 7, '=SUM(' + total_cell_range_three + ')', format1)
        sheet.write_formula(linw_row, 6, '=SUM(' + total_cell_range_four + ')', format1)
        sheet.write_formula(linw_row, 4, '=SUM(' + total_cell_range_five + ')', format1)





GstTwo_HSN_Reg_Xls('report.gsttwo_hsn_reg_xls.gstrtwo_hsn_reg_xls.xlsx', 'account.invoice')
