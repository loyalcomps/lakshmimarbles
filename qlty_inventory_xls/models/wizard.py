from odoo import models, fields, api


class qltyinventory(models.TransientModel):
    _name = "qlty.inventory.xls"
    _description = "qlty Inventory Report"

    date_inventory = fields.Datetime('Date', required=True,default=fields.Date.context_today)
    branch_ids = fields.Many2one('res.company', string='Select Branch', required=True,
                                 default=lambda self: self.env.user.company_id.id)

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'stock.history'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'qlty_inventory_xls.qlty_inventory_xls.xlsx',
                    'datas': datas,
                    'name': 'Stock Report'
                    }

    @api.multi
    def export_pdf(self):
        self.ensure_one()
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'stock.history'
        datas['form'] = self.read()[0]
        report_name = 'qlty_inventory_xls.inventory_report_pdf'
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env['report'].get_action(docids=self,
                                             report_name=report_name, data=datas)

