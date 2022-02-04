from odoo import models, fields, api


class QltySale(models.TransientModel):
    _name = "qlty.sale.xls"
    _description = "Take Away Supermart Sale Product Wise  report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Select Company',default=lambda self: self.env.user.company_id.id)
    pos_config_ids = fields.Many2many('pos.config', 'qlty_detail_configs',
                                      default=lambda s: s.env['pos.config'].search([]))
    counter_only = fields.Boolean(string='Fileter By Counter',default=True)


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
                    'report_name': 'qlty_salesreport_xls.qlty_sale_xls.xlsx',
                    'datas': datas,
                    'name': 'Detailed Sales Report'
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

        return self.env['report'].get_action(
            [], 'qlty_salesreport_xls.qlty_salesreport_pdf', data=datas)
