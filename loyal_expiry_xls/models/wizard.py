from odoo import models, fields, api


class expiry(models.TransientModel):
    _name = "loyal.expiry.xls"
    _description = "loyal_expiry_xls"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Select Company', default=lambda self: self.env.user.company_id.id )
    # type = fields.Selection([('qweb-pdf', "PDF"), ('qweb-html', "View"), ], default='qweb-pdf')


    @api.multi
    def print_report(self):
        self.ensure_one()
        datas = {'ids': self._context.get('active_ids', []), }
        report_name = 'loyal_expiry_xls.' \
                      'expiry_report_pdf'



        # report_settings = self.env['ir.actions.report.xml'].search([('report_name', '=', report_name)])
        # for settings in report_settings:
        #     settings.report_type = self.type




        datas['model'] = 'account.invoice'



        # datas['report_type'] = self.type



        datas['form'] = self.read()[0]

        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]


        # get_action(docids=self.ids,
        #            report_name=report_name)



        return self.env['report'].get_action(docids=self,
                                             report_name=report_name, data=datas)