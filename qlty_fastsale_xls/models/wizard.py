from openerp import models, fields, api


class Qltyfastsale(models.TransientModel):
    _name = "qlty.fastsale.xls"
    _description = "Fast sale report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Select Company' , default=lambda self: self.env.user.company_id.id)
    countamount = fields.Integer('Limit value',  required=True, default=10)
    selectiontype = fields.Selection([('qty', 'Quantity'), ('amt', 'Amount')], string="Select Type",
                                        required=True, default='qty')
    fstorslw = fields.Selection([('fst', 'Fast'), ('slw', 'Slow')], string="Fast Or Slow ",
                                     required=True, default='fst')
    category_id= fields.Many2one('product.category',string='Category')

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sale.order'
        datas['form'] = self.read()[0]
        if self.fstorslw == 'slw':
            reportname='Slow Sale Report'
        if self.fstorslw == 'fst':
            reportname = 'Fast Sale Report'
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'qlty_fastsale_xls.qlty_fastsale_xls.xlsx',
                    'datas': datas,
                    'name': reportname
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

            return {'type': 'ir.actions.report.xml',
                    'report_name': 'qlty_fastsale_xls.fastsale_report_pdf',
                    'datas': datas,
                    'name': 'Fast Sale PDF'
                    }

