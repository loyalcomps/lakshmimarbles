# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductPriceEditReport(models.TransientModel):
    _name = "product.price.edit.wizard"

    date_start = fields.Date('Satrt Date', required=True, default=fields.Date.context_today)
    date_end = fields.Date('End Date', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id.id)
    pos_config_ids = fields.Many2many('pos.config', 'product_price_configs',
                                      default=lambda s: s.env['pos.config'].search([]), required=True)
    user_id = fields.Many2one('res.users', string='User')
    product_id = fields.Many2one('product.product',string='Product')

    @api.multi
    def get_report_data(self):
        self.ensure_one()
        datas = {'ids': self._context.get('active_ids', []), }
        report_name = 'pos_price_edit_report.' \
                      'pos_price_edit_report_view'

        datas['model'] = 'pos.order.line'
        datas['form'] = self.read()[0]

        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]

        return self.env['report'].get_action(docids=self,
                                             report_name=report_name, data=datas)
