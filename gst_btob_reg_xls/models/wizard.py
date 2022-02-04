from openerp import models, fields, api


class GstBtoB(models.TransientModel):
    _name = "gst.btob.reg.xls"
    _description = "Gst B2B Registered Person report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Select Company')
    # current_company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env['res.company']._company_default_get('gst.btob.reg.xls'))

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.invoice'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'gst_btob_reg_xls.income_btob_xls.xlsx',
                    'datas': datas,
                    'name': 'B2BRegisteredPerson'
                    }
