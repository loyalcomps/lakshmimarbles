from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import datetime
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from odoo.tools.translate import _
import dateutil.parser
from odoo import models, fields, api
import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportInventort(models.AbstractModel):

    _name = 'report.qlty_inventory_xls.inventory_report_pdf'


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



    @api.model
    def render_html(self, docids, data=None,config_id=None):

        date_inventory = data['form']['date_inventory']


        get_lines = self.get_lines(data)

        date_object_date= datetime.strptime(date_inventory, '%Y-%m-%d %H:%M:%S').date()


        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_date.strftime('%d-%m-%Y'),

            'data': data['form'],
            'get_lines': get_lines,


        }

        return self.env['report'].render('qlty_inventory_xls.inventory_report_pdf', docargs)


