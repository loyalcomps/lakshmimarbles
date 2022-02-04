# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.TransientModel):
    _name = 'cost.change.product'

    start_date = fields.Date('Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date('End Date', required=True, default=fields.Date.context_today)
    category = fields.Many2many('product.category',string='Category')
    company_id = fields.Many2one('res.company', string='Select Branch',required=True, default=lambda self: self.env.user.company_id.id)

    @api.multi
    def export_pdf(self):
        self.ensure_one()
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'stock.move'
        datas['form'] = self.read()[0]
        report_name = 'retail_price_update.cost_change_product_report'
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env['report'].get_action(docids=self,
                                             report_name=report_name, data=datas)




