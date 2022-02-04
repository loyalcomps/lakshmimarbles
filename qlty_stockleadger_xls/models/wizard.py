from openerp import models, fields, api


class Qltystockleadger(models.TransientModel):
    _name = "qlty.stockleadger.xls"
    _description = ""

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    product_ids = fields.Many2many('product.product')
    categ_ids = fields.Many2many('product.category')
    company_id = fields.Many2one('res.company', required=True,string='Select Company' , default=lambda self: self.env.user.company_id.id)



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
                    'report_name': 'qlty_stockleadger_xls.qlty_stockleadger_xls.xlsx',
                    'datas': datas,
                    'name': 'Stock Report'
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
            return self.env['report'].get_action(self, 'qlty_stockleadger_xls.stockleadger_report_pdf', data=datas)

