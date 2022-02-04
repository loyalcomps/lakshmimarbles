# -*- coding: utf-8 -*-

from odoo import models, fields, api

class write_Off_Report(models.TransientModel):
    _name = "write.off.report"
    _description = "Write Off Report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True, string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'inventory.report.pdf'))

    stock_location = fields.Many2one('stock.location',required=True,
                                     string='Location/Branch',domain= [('usage','=','internal')])

    category_id= fields.Many2one('product.category',string='Category')

    product_id = fields.Many2one('product.product', string='Product',)

    @api.onchange('category_id')
    def product_domain(self):
        result={}
        if not self.category_id:
            result['domain'] = {'product_id': [('id', 'in', self.env['product.product'].search([]).ids)]}
            return result
        result['domain'] = {'product_id': [('categ_id', '=', self.category_id.id)]}

        return result



    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'stock.inventory'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'write_off_report.writeoff_report_xls.xlsx',
                    'datas': datas,
                    'name': 'Write Off Report'
                    }

    @api.multi
    def export_pdf(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'stock.inventory'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]

        return self.env['report'].get_action(
            [], 'write_off_report.writeoff_report_pdf', data=datas)