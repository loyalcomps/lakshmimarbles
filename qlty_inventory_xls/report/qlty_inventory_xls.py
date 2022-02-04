from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from odoo.tools.translate import _
import dateutil.parser

class qltyinventoryXls(ReportXlsx):

    def get_lines(self, data):
        lines = []
        res ={}

        date_inventory = data['form']['date_inventory']

        query = '''select max(p.name) as name,sum(sh.quantity) as quantity,round(COALESCE(SUM(sh.price_unit_on_quant * sh.quantity),0)) as valuation from stock_history sh left join product_template p on (p.id = sh.product_template_id) where date <= %s and available_in_pos = True group by sh.product_id  order by max(p.name) '''

        self.env.cr.execute(query, (date_inventory,))

        # lines = self.env.cr.dictfetchall()

        count =1
        for row in self.env.cr.dictfetchall():
            res = {
                'sl':count,
                'name': row['name'],
                'quantity': row['quantity'],
                'valuation':row['valuation'],
            }
            lines.append(res)
            count+=1

        if lines:
            return lines
        else:
            return []

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet(_('Stock'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)
        sheet.set_column(0, 1, 30)
        sheet.set_column(1, 1, 40)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 5, 40)
        company = self.env['res.company'].browse(data['form']['branch_ids']).name
        date_inventory = data['form']['date_inventory']

        format5 = workbook.add_format({'font_size': 14, 'bg_color': '#FFFFFF'})
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14})
        format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'right','bold': True})
        yellow_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,
                                        'bg_color': 'fcf22f'})
        orange_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14,
                                        'bg_color': 'f4a442'})
        blue_mark2 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 16,'bold': True,
                                        'color':'#000000','bg_color': '#1C9DB7'})
        blue_mark2.set_align('center')
        blue_mark2.set_align('vcenter')
        bold = workbook.add_format({'bold': True})
        title_style = workbook.add_format({'font_size': 14,'bold': True,
                                           'bg_color': '#FFFFCC',
                                           'bottom': 1})
        sheet_title = [_('SL/NO'),
                       _('Product'),
                       _('Stock'),
                       _('Inventory Valuation'),
                       ]
        b = str(date_inventory)
        d = dateutil.parser.parse(b).date()

        date_in = datetime.strptime(str(d), '%Y-%m-%d').strftime('%m/%d/%y')

        date = "Inventory At " + str(date_in)

        # sheet.set_row(0, None, None, {'collapsed': 1})
        sheet.merge_range('A1:D1', company, blue_mark2)
        sheet.merge_range('A2:D2',"Stock Report",blue_mark2)
        sheet.merge_range('A3:D3',date,blue_mark2)

        # sheet.merge_range('E1:G1',date_start + '-' + date_end, blue_mark2)
        sheet.write_row(3, 0, sheet_title, title_style)

        linw_row =4

        line_column = 0

        for line in self.get_lines(data):
            sheet.write(linw_row, line_column, line['sl'], font_size_8)
            sheet.write(linw_row, line_column+1, line['name'], font_size_8)
            sheet.write(linw_row, line_column+2, line['quantity'], font_size_8)
            sheet.write(linw_row, line_column+3, line['valuation'], font_size_8)

            linw_row = linw_row +1
            line_column=0
        #
        #
        sheet.write(linw_row, 0, "TOTAL", format1)

        am_cell_range = xl_range(4,2,linw_row-1,2)
        ex_cell_range = xl_range(4,3,linw_row-1,3)

        sheet.write_formula(linw_row, 2, '=SUM('+am_cell_range+')')
        sheet.write_formula(linw_row, 3, '=SUM('+ex_cell_range+')')


qltyinventoryXls('report.qlty_inventory_xls.qlty_inventory_xls.xlsx', 'stock.history')
