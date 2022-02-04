from datetime import datetime
from odoo import api, fields, models

class qltycashbook(models.TransientModel):
    _name = "qlty.cashbook.xls"
    _description = "qlty cash book"

    @api.model
    def _default_journal(self):

        domain = [('type', '=', 'cash')]
        return self.env['account.journal'].search(domain, limit=1)
    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    branch_ids = fields.Many2one('res.company', string='Select Branch',required=True, default=lambda self: self.env.user.company_id.id)
    journal_ids = fields.Many2one('account.journal', string='Select Journal',default=_default_journal,required=True )


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
                    'report_name': 'qlty_cashbook_xls.cashbook_report_xls.xlsx',
                    'datas': datas,
                    'name': 'Cashbook'
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

        return self.env['report'].get_action(self, 'qlty_cashbook_xls.cashbook_report_pdf', data=datas)
        # if context.get('xls_export'):
        #     return {'type': 'ir.actions.report.xml',
        #             'report_name': 'qlty_cashbook_xls.cashbook_report_pdf',
        #             'datas': datas,
        #             'name': 'CashBookPDF'
        #             }








