from openerp import models, fields, api

class possale(models.TransientModel):
    _name = "gst.possale.xls"
    _description = "possale"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    branch_ids = fields.Many2one('res.company', string='Select Branch',required=True, default=lambda self: self.env.user.company_id.id)

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
                    'report_name': 'gst_possale_xls.possale_report_xls.xlsx',
                    'datas': datas,
                    'name': 'GST POS Sale '
                    }
