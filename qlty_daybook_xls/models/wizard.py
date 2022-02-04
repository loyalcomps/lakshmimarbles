from openerp import models, fields, api


class qltydaybook(models.TransientModel):
    _name = "qlty.daybook.xls"
    _description = "qlty day book"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    branch_ids = fields.Many2one('res.company', string='Select Branch',required=True, default=lambda self: self.env.user.company_id.id)
    detailed = fields.Boolean(string='Detailed',default=False)

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.move'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'qlty_daybook_xls.daybook_report_xls.xlsx',
                    'datas': datas,
                    'name': 'DayBook'
                    }

    @api.multi
    def export_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.move'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env['report'].get_action(self, 'qlty_daybook_xls.daybook_report_pdf', data=datas)
        # if context.get('xls_export'):
        #     return {'type': 'ir.actions.report.xml',
        #             'report_name': 'qlty_daybook_xls.daybook_report_pdf',
        #             'datas': datas,
        #             'name': 'DayBookPDF'
        #             }
