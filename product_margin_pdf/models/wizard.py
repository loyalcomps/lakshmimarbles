from openerp import models, fields, api


class Productmargin(models.TransientModel):
    _name = "product.margin.pdf"
    _description = "Monthly Sales report"

    date_start = fields.Date('Date', required=True, default=fields.Date.context_today)
    date_end = fields.Date('Date End', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True, string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'product.margin.pdf'))


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
                [], 'product_margin_pdf.qlty_brand_pdf', data=datas)

