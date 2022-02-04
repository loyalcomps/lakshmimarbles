from odoo import models, fields, api


class seveninventory(models.TransientModel):
    _name = "seven.deadstock.xls"
    _description = "Seven Deadstock  report"

    date_start = fields.Date('Start Date', required=True, default=fields.Date.context_today)
    date_end = fields.Date('End Date', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True, string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('take.deadstock'))
    wh_id = fields.Many2one('stock.warehouse', string='Warehouse')
    min_qty = fields.Float(string="Minimum Quantity")

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'product.product'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'seven_deadstock_xls.seven_deadstock_xls.xlsx',
                    'datas': datas,
                    'name': ' Dead Stock Report'
                    }

    @api.multi
    def export_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'product.product'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'seven_deadstock_xls.seven_deadstock_pdf',
                    'datas': datas,
                    'name': 'Dead Stock Report'
                    }
