from openerp import models, fields, api


class QltyCat(models.TransientModel):
    _name = "qlty.productsale.xls"
    _description = "Quality Super Bazar Product wise Sale report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Company',
                default=lambda self: self.env['res.company']._company_default_get('qlty.productsale.xls'))
    product_id = fields.Many2one('product.product', string='Product', required=True)




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
                    'report_name': 'qlty_productsale_xls.qlty_productsale_xls.xlsx',
                    'datas': datas,
                    'name': 'Date Wise Sale Wise Report'
                    }

    @api.multi
    def export_pdf(self):
        self.ensure_one()
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sale.order'
        datas['form'] = self.read()[0]
        report_name = 'qlty_productsale_xls.productsale_report_pdf'
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env['report'].get_action(docids=self,
                                             report_name=report_name, data=datas)
