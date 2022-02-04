from openerp import models, fields, api

class Grand_sale_details(models.TransientModel):
    _name = "grand.sale.details.xls"
    _description = "Grand sale Details"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    branch_ids = fields.Many2one('res.company', string='Select Branch',required=True, default=lambda self: self.env.user.company_id.id)
    pos_config_ids = fields.Many2many('pos.config', 'grand_detail_configs',
                                      default=lambda s: s.env['pos.config'].search([]))
    counter_only = fields.Boolean(string='Fileter By Counter', default=True)


    @api.multi
    def export_pdf(self):
        self.ensure_one()
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sale.order'
        datas['form'] = self.read()[0]
        report_name = 'grand_sale_detail_xls.grand_sale_detail_pdf'
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env['report'].get_action(docids=self,
                                             report_name=report_name, data=datas)
