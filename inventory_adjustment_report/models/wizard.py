from odoo import models, fields, api


class inventory_report(models.TransientModel):
    _name = "inventory.report.pdf"
    _description = "Inventory Report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True, string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'inventory.report.pdf'))

    category_only = fields.Boolean(string='All Category')



    stock_location = fields.Many2one('stock.location',required=True,
                                     string='Select Location',domain= [('usage','=','internal')])

    category_id= fields.Many2one('product.category',string='Category')

    product_id = fields.Many2one('product.product', string='Product')



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
                    'report_name': 'inventory_adjustment_report.inventory_report_xls.xlsx',
                    'datas': datas,
                    'name': 'Inventory Report'
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
            [], 'inventory_adjustment_report.inv_report_pdf', data=datas)
