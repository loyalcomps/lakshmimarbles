from openerp import models, fields, api


class QltyCat(models.TransientModel):
    _name = "qlty.cat.xls"
    _description = "Take Away Supermart Sale Category Wise  report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Select Company', default=lambda self: self.env.user.company_id.id)
    category_id= fields.Many2one('pdct.category',string='Category')


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
                    'report_name': 'qlty_category_xls.qlty_category_xls.xlsx',
                    'datas': datas,
                    'name': 'Category Wise Report'
                    }
