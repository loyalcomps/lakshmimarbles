from odoo import models, fields, api


class Vendorbill(models.TransientModel):
    _name = "bill.payment.xls"
    _description = "Paymeny Details"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Company',
                default=lambda self: self.env['res.company']._company_default_get('bill.payment.xls'))

    vendor_id = fields.Many2one('res.partner', required=True,string='Vendor',domain="[('supplier','=',True)]" )





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
                    'report_name': 'bill_payment_xls.bill_payment_xls.xlsx',
                    'datas': datas,
                    'name': 'Payment Report'
                    }

    @api.multi
    def export_pdf(self):
        self.ensure_one()
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.move'
        datas['form'] = self.read()[0]
        report_name = 'bill_payment_xls.payment_report_pdf'
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env['report'].get_action(docids=self,
                                             report_name=report_name, data=datas)
