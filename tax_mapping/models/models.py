# -*- coding: utf-8 -*-

from odoo import models, fields, api

class VToCTaxMapping(models.Model):
    _name = 'vtoc.tax.mapping'

    name = fields.Char(string='Tax Mapping', required=True)
    active = fields.Boolean(string = 'Active', default=True,
                            help="By unchecking the active field, you may hide Tax Mapping without deleting it.")
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env['res.company']._company_default_get('vtoc.tax.mapping'),required=True)
    # auto_apply = fields.Boolean(string='Detect Automatically', help="Apply automatically this Tax Mapping.")
    tax_ids = fields.One2many('tax.mapping.taxes', 'vtoc_tax_mapping_id', string='Tax Mapping', copy=True)

    @api.model  # noqa
    def map_tax(self, taxes):
        result = self.env['account.tax'].browse()
        for tax in taxes:
            tax_count = 0
            for t in self.tax_ids:
                if t.vendor_tax_id == tax:
                    tax_count += 1
                    if t.customer_tax_id:
                        result |= t.customer_tax_id
            # if not tax_count:
            #     result |= tax
        return result

class VToCTaxMappingTaxes(models.Model):
    _name = 'tax.mapping.taxes'
    _description = 'Taxes'
    _rec_name = 'vtoc_tax_mapping_id'


    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env['res.company']._company_default_get('vtoc.tax.mapping'))
    vtoc_tax_mapping_id = fields.Many2one('vtoc.tax.mapping', string='Fiscal Position',
        required=True, ondelete='cascade')
    vendor_tax_id = fields.Many2one('account.tax', string='Vendor Tax on Product', required=True)
    customer_tax_id = fields.Many2one('account.tax', string='Customer Tax to Apply')

