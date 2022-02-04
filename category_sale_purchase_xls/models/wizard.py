from openerp import models, fields, api


class QltyCat(models.TransientModel):
    _name = "category.sale.purchase"
    _description = "Quality Super Bazar Category wise Sale - Purchase report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Company',
                default=lambda self: self.env['res.company']._company_default_get('category.sale.purchase'))



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
                    'report_name': 'category_sale_purchase_xls.category_sale_purchase_xls.xlsx',
                    'datas': datas,
                    'name': 'Category Wise Sale- Purchase Report'
                    }
