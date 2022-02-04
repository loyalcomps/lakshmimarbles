# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CogReport(models.TransientModel):
    _name = 'cog.report'

    date_start = fields.Date('Date from', required=True, default=fields.Date.context_today)
    date_end = fields.Date('Date to', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True, string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'cog.report'))
    gp_filter = fields.Float('Below GP%',default = 0)

    @api.multi
    def export_report(self):
        self.ensure_one()
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.invoice'
        datas['form'] = self.read()[0]
        report_name = 'cog_report.cog_report_pdf'
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env['report'].get_action(docids=self,
                                             report_name=report_name, data=datas)

