from openerp import models, fields, api


class Brandsalereport(models.TransientModel):
    _name = "negative.report.pdf"
    _description = "Negative inventory"

    date_start = fields.Date('Date', required=True, default=fields.Date.context_today)
    # date_end = fields.Date('Date End', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True, string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'negative.report.pdf'))


    #
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
                    'report_name': 'negative_inventory_report.qlty_inventory_xls.xlsx',
                    'datas': datas,
                    'name': 'Negative inventory'
                    }

    @api.multi
    def export_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sale.order'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env['report'].get_action(
                [], 'negative_inventory_report.qlty_inventory_pdf', data=datas)

