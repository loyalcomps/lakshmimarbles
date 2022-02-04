from odoo import models, fields, api


class TakeFast(models.TransientModel):
    _name = "take.fastslow.xls"
    _description = "Take Away Supermart Fast/Slow Move report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Select Company',default=lambda self: self.env['res.company']._company_default_get('take.fastslow.xls'))
    slow_move = fields.Boolean(string='Slow Move')
    store_id = fields.Many2many('stock.warehouse', string='Store', required=True)

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sale.order'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'take_fastslowmove_xls.take_fastslow_xls.xlsx',
                    'datas': datas,
                    'name': 'Fast/Slow Move Report'
                    }
