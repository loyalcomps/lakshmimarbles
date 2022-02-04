from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from odoo.tools.translate import _


class qltyinvoiceXls(ReportXlsx):


    def get_partnersum(self, data):
        lines = []
        res = {}

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_id = data['form']['branch_id']
        type = data['form']['type']

        query = '''select max(i.date_invoice) as date,max(p.name) as partner,sum(i.amount_total) as total
    from account_invoice i left join res_partner p on (p.id = i.partner_id) where i.type= %s and i.date_invoice between %s and %s and i.company_id = %s and i.state in ('paid','open') group by p.name order by p.name  '''
        self.env.cr.execute(query, (type, date_start, date_end, branch_id))

        # lines = self.env.cr.dictfetchall()

        for row in self.env.cr.dictfetchall():
            res = {
                'date_invoice': row['date'],
                'partner': row['partner'],
                'amount_total': row['total'],
            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []
    def get_lines(self, data):
        lines = []
        res ={}

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_id = data['form']['branch_id']
        type = data['form']['type']

        query = '''select i.date_invoice,i.number,p.name,i.reference,i.amount_tax,i.amount_untaxed,i.amount_discount,i.amount_total
from account_invoice i left join res_partner p on (p.id = i.partner_id) where i.type= %s and i.date_invoice between %s and %s and i.company_id = %s and i.state in ('paid','open') order by date_invoice
            '''
        self.env.cr.execute(query,(type,date_start,date_end,branch_id))

        # lines = self.env.cr.dictfetchall()

        for row in self.env.cr.dictfetchall():
            res = {
                'date_invoice':row['date_invoice'],
                'number':row['number'],
                'name': row['name'],
                'reference': row['reference'],
                'amount_tax': row['amount_tax'],
                'amount_untaxed': row['amount_untaxed'],
                'amount_total': row['amount_total'],
                'amount_discount': row['amount_discount'],
            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('INVOICE'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 1, 15)
        sheet.set_column(1, 1, 40)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 5, 20)
        sheet.set_column(6, 7, 20)
        company = self.env['res.company'].browse(data['form']['branch_id']).name
        company_address = self.env['res.company'].browse(data['form']['branch_id']).street
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})
        format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right','bold': True})
        yellow_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,
                                        'bg_color': 'fcf22f'})
        orange_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,
                                        'bg_color': 'f4a442'})
        blue_mark2 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,'bold': True,
                                        'color':'000000','bg_color': 'bdb3ca'})
        blue_mark3 = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True,
             'color': '000000', 'bg_color': 'bdb3ca','align':'center'})
        bold = workbook.add_format({'bold': True})
        title_style = workbook.add_format({'font_size': 14,'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})

        if not data['form']['consolidated']:

            sheet_title = [_('Date'),
                       _('Bill No'),
                       _('Reference No'),
                       _('Partner'),
                       _('Taxable Amount'),
                       _('Tax Amount'),
                       _('Discount'),
                       _('Amount')
                       ]

            sheet.merge_range('B1:E1', company, blue_mark3)
            sheet.merge_range('B2:E2', company_address, blue_mark3)
            sheet.merge_range('B3:E3', "INVOICE Report", blue_mark3)
            sheet.merge_range('B4:E4', date_start + '-' + date_end, blue_mark3)

            sheet.write_row(4, 0, sheet_title, title_style)

            linw_row = 5

            line_column = 0

            for line in self.get_lines(data):
                sheet.write(linw_row, line_column, line['date_invoice'], font_size_8)
                sheet.write(linw_row, line_column+1, line['number'], font_size_8)
                sheet.write(linw_row, line_column+2, line['reference'], font_size_8)
                sheet.write(linw_row, line_column+3, line['name'], font_size_8)
                sheet.write_number(linw_row, line_column+4, line['amount_untaxed'], font_size_8)
                sheet.write_number(linw_row, line_column+5, line['amount_tax'], font_size_8)
                sheet.write_number(linw_row, line_column+6, line['amount_discount'], font_size_8)
                sheet.write_number(linw_row, line_column+7, line['amount_total'], font_size_8)


                linw_row = linw_row +1
                line_column=0
        
        
        
            sheet.merge_range(linw_row,0,linw_row,3, "TOTAL", format1)
            am_cell_range = xl_range(2,7,linw_row-1,7)
            ex_cell_range = xl_range(2,4,linw_row-1,4)
            pex_cell_range = xl_range(2,5,linw_row-1,5)
            wpex_cell_range = xl_range(2,6,linw_row-1,6)
            sheet.write_formula(linw_row, 4, '=SUM('+ex_cell_range+')')
            sheet.write_formula(linw_row, 5, '=SUM('+pex_cell_range+')')
            sheet.write_formula(linw_row, 6, '=SUM('+wpex_cell_range+')')
            sheet.write_formula(linw_row, 7, '=SUM('+am_cell_range+')')

        else:
            sheet_title = [_('Vendor'),
                           _('Amount')
                           ]

            sheet.merge_range('B1:E1', company, blue_mark3)
            sheet.merge_range('B2:E2', company_address, blue_mark3)
            sheet.merge_range('B3:E3', "Vendor Wise Total Report", blue_mark3)
            sheet.merge_range('B4:E4', date_start + '-' + date_end, blue_mark3)

            sheet.write_row(4, 1, sheet_title, title_style)

            linw_row = 5

            line_column = 0

            for line in self.get_partnersum(data):
                sheet.write(linw_row, line_column + 1, line['partner'], font_size_8)
                sheet.write(linw_row, line_column + 2, line['amount_total'], font_size_8)

                linw_row = linw_row + 1
                line_column = 0

            sheet.merge_range(linw_row, 0, linw_row, 1, "TOTAL", format1)
            am_cell_range = xl_range(2, 2, linw_row - 1, 2)
            sheet.write_formula(linw_row, 2, '=SUM(' + am_cell_range + ')')


qltyinvoiceXls('report.qlty_invoice_xls.qlty_invoice_xls.xlsx', 'account.invoice')
