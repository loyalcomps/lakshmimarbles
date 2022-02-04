from openerp import models, fields, api


class pos_cashcardsession(models.TransientModel):
    _name = "pos.cashcardsession.xls"
    _description = " Date And Session wise Sale report with card And cash"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Company',
                default=lambda self: self.env['res.company']._company_default_get('qlty.sale.purchase.xls'))
    pos_config_ids = fields.Many2one('pos.config', string='Select Counter')
    counter_only = fields.Boolean(string='Filter By Counter', default=False)


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
                    'report_name': 'pos_cashcardsession_xls.pos_cashcardsession_xls.xlsx',
                    'datas': datas,
                    'name': 'POS-Sale-Report'
                    }
