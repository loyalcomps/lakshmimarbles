from openerp import models, fields, api


class Brandsalereport(models.TransientModel):
    _name = "brandwisesale.report.pdf"
    _description = "Brand sale report"

    date_start = fields.Date('Date', required=True, default=fields.Date.context_today)
    date_end = fields.Date('Date End', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True, string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'brandwisesale.report.pdf'))
    # company_id = fields.Many2one('res.company', string='Select Company')
    brand_id = fields.Many2one('product.brand',string="Brand")
    brand_only = fields.Boolean(string='Fileter By Brand', default=True)
    category_id = fields.Many2one('product.category', string='Category')


    #
    # @api.multi
    # def export_xls(self):
    #     context = self._context
    #     datas = {'ids': context.get('active_ids', [])}
    #     datas['model'] = 'sale.order'
    #     datas['form'] = self.read()[0]
    #     for field in datas['form'].keys():
    #         if isinstance(datas['form'][field], tuple):
    #             datas['form'][field] = datas['form'][field][0]
    #     if context.get('xls_export'):
    #         return {'type': 'ir.actions.report.xml',
    #                 'report_name': 'brandsale_report_xls.qlty_brand_xls.xlsx',
    #                 'datas': datas,
    #                 'name': 'Brand Wise Report'
    #                 }

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
                [], 'brandwise_report_pdf.qlty_brand_pdf', data=datas)

