from openerp import models, fields, api


class GstTwoHSN(models.TransientModel):
    _name = "gsttwo.hsn.reg.xls"
    _description = "GSTR Two HSN  report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Select Company')

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
                    'report_name': 'gsttwo_hsn_reg_xls.gstrtwo_hsn_reg_xls.xlsx',
                    'datas': datas,
                    'name': 'GSTR2_HSN'
                    }
