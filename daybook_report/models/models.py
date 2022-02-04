# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DayBook(models.TransientModel):
    _name = "day.book"
    _description = "Day book"

    date_start = fields.Date('Start Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('End Date',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string='Select Company',required=True, default=lambda self: self.env.user.company_id.id)


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
                    'report_name': 'daybook_report.daybook_report_xls.xlsx',
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
        return self.env['report'].get_action(self, 'daybook_report.daybook_report_pdf', data=datas)