# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ConsolidatedSales(models.TransientModel):
    _name = "consolidated.sale.report"
    _description = "consolidated sale report"

    date_start = fields.Date('Date', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True, string='Select Company',
                                 default=lambda self: self.env.user.company_id.id)
    stock_loc = fields.Many2one('stock.location',  string='Select Branch',
                                  )
    # pos_config_ids = fields.Many2many('pos.config', 'consolidated_sale_configs',
    #                                   default=lambda s: s.env['pos.config'].search([]))
    counter_only = fields.Boolean(string='Fileter By Branch', default=True)

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
                    'report_name': 'consolidated_sale_report.sale_xls.xlsx',
                    'datas': datas,
                    'name': 'Consolidated Sale Report'
                    }

    @api.multi
    def export_pdf(self):
        self.ensure_one()
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.move'
        datas['form'] = self.read()[0]
        report_name = 'consolidated_sale_report.sale_report_pdf'
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env['report'].get_action(docids=self,
                                             report_name=report_name, data=datas)