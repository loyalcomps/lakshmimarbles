# -*- coding: utf-8 -*-

from odoo import models, fields, api

class payment_term_report(models.TransientModel):
    _name = 'payment.term.report'

    date_start = fields.Date('Start Date', required=True, default=fields.Date.context_today)
    date_end = fields.Date('End Date', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string='Select Branch', required=True,
                                 default=lambda self: self.env.user.company_id.id)

    vendor_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Filter Vendor',domain="[('supplier','=','True')]"
    )

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
                    'report_name': 'payment_term_report.payment_term_xls.xlsx',
                    'datas': datas,
                    'name': 'Payment Term'
                    }

    @api.multi
    def export_pdf(self):
        self.ensure_one()
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.move'
        datas['form'] = self.read()[0]
        report_name = 'payment_term_report.payment_term_pdf'
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env['report'].get_action(docids=self,
                                             report_name=report_name, data=datas)



