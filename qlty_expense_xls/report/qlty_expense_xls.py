from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _


class qltyexpenseXls(ReportXlsx):

    def get_lines(self, data):
        lines = []
        res ={}

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        branch_ids = data['form']['branch_ids']

        exp_ids = self.env["qlty.expense"].search([('date', '>=', date_start),
                                                      ('date', '<=', date_end),
                                                      ('company_id', '=', branch_ids),
                                                      ('state', '=', 'posted'),
                                                   ('is_petty', '=', True)
                                                      ]).sorted('date')

        for j in exp_ids:
            res = {
                'date' :j.date,
                'name' :j.name,
                'total' :j.total,
                'state' :j.state,



            }

            lines.append(res)

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Expense'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 1, 20)
        sheet.set_column(1, 1, 30)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 5, 20)
        company = self.env['res.company'].browse(data['form']['branch_ids']).name
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
        bold = workbook.add_format({'bold': True})
        title_style = workbook.add_format({'font_size': 14,'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})
        sheet_title = [_('Date'),
                       _('Particulars'),
                       _('Expense'),
                       _('State')
                       ]
        
        # sheet.set_row(0, None, None, {'collapsed': 1})
        sheet.merge_range('A1:B1',"Petty Cash Expense  Report",blue_mark2)
        sheet.merge_range('C1:D1',date_start + '-' + date_end, blue_mark2)
        # sheet.merge_range('E1:G1',date_start + '-' + date_end, blue_mark2)
        sheet.write_row(1, 0, sheet_title, title_style)

        linw_row =2

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['date'], font_size_8)
            sheet.write(linw_row, line_column+1, line['name'], font_size_8)
            sheet.write(linw_row, line_column+2, line['total'], font_size_8)
            sheet.write(linw_row, line_column+3, line['state'], font_size_8)
            # sheet.write_number(linw_row, line_column+4, line['amount'], font_size_8)
            # sheet.write_number(linw_row, line_column+5, line['expense'], font_size_8)
            # if line['state'] == 'approve':
            #
            #     sheet.write(linw_row, line_column+6, line['state'], yellow_mark)
            # elif line['state'] == 'wait':
            #
            #     sheet.write(linw_row, line_column+6, line['state'], orange_mark)
            # else:
            #     sheet.write(linw_row, line_column+6, line['state'], font_size_8)

            linw_row = linw_row +1
            line_column=0
        # sheet.write_row(linw_row, 2, "TOTAL", format1)



        sheet.write(linw_row, 0, "TOTAL", format1)

        am_cell_range = xl_range(2,2,linw_row-1,2)
        # ex_cell_range = xl_range(2,5,linw_row-1,5)

        sheet.write_formula(linw_row, 2, '=SUM('+am_cell_range+')')
        # sheet.write_formula(linw_row, 5, '=SUM('+ex_cell_range+')')


qltyexpenseXls('report.qlty_expense_xls.expense_report_xls.xlsx', 'account.move')
