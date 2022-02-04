# -*- coding: utf-8 -*-

from odoo import models, fields, api

class VendorPL(models.TransientModel):
    _name = "vendor.pl"
    _description = "Vendor Wise Profit And Loss report"

    date_start = fields.Date('Start Date', required=True, default=fields.Date.context_today)
    date_end = fields.Date('End Date', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True, string='Select Company',
                                 default=lambda self: self.env.user.company_id.id)
    vendor_id = fields.Many2many(relation='vendor_pl_rel',
    comodel_name='res.partner',column1='partner_id', column2='vendor_pl_id',
                                 required=True, string='Vendor', domain="[('supplier','=',True),('parent_id','=',False)]")
    vendor_contact_id = fields.Many2many(relation='contact_pl_rel',
    comodel_name='res.partner',column1='partner_id', column2='vendor_pl_id', string='Vendor Contact',)
    product_id = fields.Many2many('product.product', string='Product',
                                 domain="[('sale_ok','=',True),('purchase_ok','=',True)]")

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sale.order'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'vendor_pandl_report.vendorwise_pandl_xls.xlsx',
                    'datas': datas,
                    'name': 'Vendor Wise Report'
                    }

    @api.multi
    def export_pdf(self):
        self.ensure_one()
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sale.order'
        datas['form'] = self.read()[0]
        report_name = 'vendor_pandl_report.vendorwise_pandl_pdf'
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env['report'].get_action(docids=self,
                                             report_name=report_name, data=datas)