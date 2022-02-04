# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):

        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        company_id = self.company_id or self.env.user.company_id
        tax_mapping_obj = self.env['vtoc.tax.mapping'].search([('active','=',True),('company_id','=',company_id.id)],limit=1)
        for l in line:

            taxes = l.taxes_id.filtered(lambda r: r.company_id == company_id)
            if l.product_id.taxes_id:
                customer_tax_id = l.product_id.taxes_id
            else:
                customer_tax_id = tax_mapping_obj.map_tax(taxes)
                _logger.info("Vendor to customer tax mapping has been done")
            var = {

                'customer_tax_id': customer_tax_id,


            }
        res.update(var)
        return res

# class AccountInvoiceLine(models.Model):
#     _inherit = "account.invoice.line"
#
#     @api.onchange('product_id')
#     def _onchange_product_id(self):
#         res = super(AccountInvoiceLine, self)._onchange_product_id()
#         company_id = self.company_id or self.env.user.company_id
#         tax_mapping_obj = self.env['vtoc.tax.mapping'].search(
#             [('active', '=', True), ('company_id', '=', company_id.id)], limit=1)
#         if self.product_id.taxes_id:
#             self.customer_tax_id = self.product_id.taxes_id
#         else:
#             if self.product_id.supplier_taxes_id:
#                 taxes = self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id == company_id)
#                 self.customer_tax_id = tax_mapping_obj.map_tax(taxes)




