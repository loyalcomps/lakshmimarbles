# -*- coding: utf-8 -*-

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from Number2Words import Number2Words
  
class GstModule(models.Model):
    _name ='gst.tax'
    taxable_value=fields.Float(string="Taxable Value",digits=(16, 4)) 
    state_tax=fields.Float(digits=dp.get_precision('State GST'),string="State GST")
    state_amount=fields.Float(string="State GST Amount",digits=(16, 4))
    central_tax=fields.Float(digits=dp.get_precision('Central GST'),string="Central GST")
    central_amount=fields.Float(string="Central GST Amount",digits=(16, 4))
    integrated_tax=fields.Float(digits=dp.get_precision('Integrated GST'),string="Integrated GST")
    integrated_amount=fields.Float(string="Integrated GST Amount",digits=(16, 4))
    cess_amount = fields.Float(string="Cess", digits=(16, 4))
    invoice_id=fields.Many2one("account.invoice",string="Invoice")
    tax=fields.Char(string="Tax")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('gst.tax'))
    hsn = fields.Char(string="HSN")

class InvoiceInherit(models.Model):
    _inherit='account.invoice'
      
    gst_tax_ids=fields.One2many("gst.tax","invoice_id",string="GST tax id")

    def _get_amount(self, amt):

        amt = amt
        amount_in_word = Number2Words().convertNumberToWords(amt)
        return amount_in_word
    
    @api.multi
    def compute_taxes(self):
        res=super(InvoiceInherit, self).compute_taxes()
        

        gst_tax_lines = self.env['gst.tax']
        
        
        for invoice in self:
            # Delete non-manual tax lines
            self._cr.execute("DELETE FROM gst_tax WHERE invoice_id=%s ", (invoice.id,))
            self.invalidate_cache()

            # Generate one tax line per tax, however many invoice lines it's applied to
            taxes = invoice.calculate_taxes_values()

            # Create new tax lines
            
            gst_val ={}
            for key,tax in taxes.items():
                if self.partner_id.state_code!=self.company_id.state_code:
                    gst_val={
                        'invoice_id': self.id,
                        'tax': self.env['account.tax'].browse(tax['tax_id']).name,
                        'integrated_tax':self.env['account.tax'].browse(tax['tax_id']).amount ,
                        'integrated_amount': tax['amount']-tax['cess_amount'],
                        'hsn' : key,
                        'cess_amount':tax['cess_amount'],
                        
                        'taxable_value':tax['base']
                        }
                else:
                    gst_val={
                        'invoice_id': self.id,
                        'tax': self.env['account.tax'].browse(tax['tax_id']).name,
                        'state_tax':self.env['account.tax'].browse(tax['tax_id']).amount/2 ,
                        'hsn': key,
                        'state_amount': (tax['amount']-tax['cess_amount'])/2,
                        'central_tax':self.env['account.tax'].browse(tax['tax_id']).amount/2 ,
                        'central_amount': (tax['amount']-tax['cess_amount'])/2,
                        'taxable_value':tax['base'],
                        'cess_amount': tax['cess_amount'],
                        }
            
#                 gst_tax_lines += gst_tax_lines.new(gst_val)
                gst_tax_lines.create(gst_val)
#             self.gst_tax_ids = gst_tax_lines

        return res

#     @api.onchange('tax_line_ids')
#     def _onchange_tax_line_ids(self):
# #         taxes_grouped = self.get_taxes_values()
#         gst_tax_lines = self.gst_tax_ids.browse([])
#         val ={}
#         for tax in self.tax_line_ids:
#             val={
#                 'invoice_id': self.id,
#                 'state_tax': tax.tax_id.amount,
#                 'state_amount':tax.amount ,
#                 'central_tax': tax.tax_id.amount,
#                 'central_amount': tax.amount,
#                 'integrated_tax':tax.tax_id.amount ,
#                 'integrated_amount': tax.amount,               
#                 }
#             
#             gst_tax_lines += gst_tax_lines.new(val)
#         self.gst_tax_ids = gst_tax_lines
#         return
#     @api.onchange('invoice_line_ids','tax_line_ids','amount_total')
#     @api.multi
#     @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount')

    @api.onchange('invoice_line_ids','tax_line_ids','amount_total')
    def onchange_invoice_line_ids(self):
        taxes_grouped = self.calculate_taxes_values()
        gst_tax_lines = self.gst_tax_ids.browse([])
        gst_val ={}
        for key,tax in taxes_grouped.items():
            if self.partner_id.state_code!=self.company_id.state_code:
                gst_val={
                    'invoice_id': self.id,
                    'tax': self.env['account.tax'].browse(tax['tax_id']).name,
                    'integrated_tax':self.env['account.tax'].browse(tax['tax_id']).amount ,
                    'integrated_amount': (tax['amount']-tax['cess_amount']),
                    'hsn': key,
                    'taxable_value':tax['base'],
                    'cess_amount': tax['cess_amount'],
                    }
            else:
                gst_val={
                    'invoice_id': self.id,
                    'tax': self.env['account.tax'].browse(tax['tax_id']).name,
                    'state_tax': self.env['account.tax'].browse(tax['tax_id']).amount/2 ,
                    'hsn': key,
                    'state_amount': (tax['amount']-tax['cess_amount'])/2,
                    'central_tax': self.env['account.tax'].browse(tax['tax_id']).amount/2 ,
                    'central_amount': (tax['amount']-tax['cess_amount'])/2,
                    'taxable_value':tax['base'],
                    'cess_amount': tax['cess_amount'],
                    }
            gst_tax_lines += gst_tax_lines.new(gst_val)
        self.gst_tax_ids = gst_tax_lines
        return
    
        
#         gst_val ={}
#         for line in self.invoice_line_ids:
#             price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#             key=line.product_id.hsn
#             
#             taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
#             for tax in taxes:
#                 val = self._prepare_tax_line_vals(line, tax)
#                 if self.partner_id.out_of_state==True:
#                     gst_val={
#                         'invoice_id': self.id,
#                         'integrated_tax':self.env['account.tax'].browse(val['tax_id']).amount ,
#                         'integrated_amount': val['amount'],
#                         'taxable_value':val['base']
#                         }
#                 else:
#                     gst_val={
#                         'invoice_id': self.id,
#                         'state_tax':self.env['account.tax'].browse(val['tax_id']).amount/2 ,
#                         'state_amount': val['amount']/2,
#                         'central_tax':self.env['account.tax'].browse(val['tax_id']).amount/2 ,
#                         'central_amount': val['amount']/2,
#                         'taxable_value':val['base']
#                         }
#                 gst_tax_lines += gst_tax_lines.new(gst_val)
# #         for tax in self.tax_line_ids:
# #             val={
# #                 'invoice_id': self.id,
# #                 'state_tax': tax.tax_id.amount,
# #                 'state_amount':tax.amount ,
# #                 'central_tax': tax.tax_id.amount,
# #                 'central_amount': tax.amount,
# #                 'integrated_tax':tax.tax_id.amount ,
# #                 'integrated_amount': tax.amount,               
# #                 }
# #             
#             
    def _prepare_tax_line_vals(self, line, tax):
        res = super(InvoiceInherit, self)._prepare_tax_line_vals(line,tax)
        """ Prepare values to create an account.invoice.tax line

        The line parameter is an account.invoice.line, and the
        tax parameter is the output of account.tax.compute_all().
        """
        vals = {
            'invoice_id': self.id,
            'name': tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'base': tax['base'],
            'cess': 'cess' in tax and tax['cess'] or False,
            'cess_amount': tax['amount'] if 'cess' in tax and tax['cess'] or False else 0,
            'manual': False,
            'sequence': tax['sequence'],
            'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
            'account_id': self.type in ('out_invoice', 'in_invoice') and (
                tax['account_id'] or line.account_id.id) or (tax['refund_account_id'] or line.account_id.id),
        }

        # If the taxes generate moves on the same financial account as the invoice line,
        # propagate the analytic account from the invoice line to the tax line.
        # This is necessary in situations were (part of) the taxes cannot be reclaimed,
        # to ensure the tax move is allocated to the proper analytic account.
        if not vals.get('account_analytic_id') and line.account_analytic_id and vals[
            'account_id'] == line.account_id.id:
            vals['account_analytic_id'] = line.account_analytic_id.id

        return vals
    
    @api.multi
    def calculate_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.cess_tax_id:
                taxes = line.invoice_line_tax_ids.compute_cess_tax(price_unit, self.currency_id, line.quantity,
                                                     line.product_id, self.partner_id,
                                                     cess_tax_id=line.cess_tax_id)['taxes']
            else:
                taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']

            key =line.product_id.hsn

            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)

                # key=self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['cess_amount'] += val['cess_amount']
                    if val['cess']==False:
                        tax_grouped[key]['base'] += val['base']
        return tax_grouped
    
#     @api.depends('tax_line_ids.amount') 
#     def counting_gst_amount(self):
# #         state 
#         for i in self.tax_line_ids:
#             if self.partner_id.out_of_state==True:
#                 integrated_tax=i.tax_id.amount
#                 integrated_amount=i.amount
#              else:
#                 state_tax=central_tax=i.tax_id.amount/2
#                 state_amount=central_amount=i.amount/2
     
class ResPartner(models.Model):
    _inherit='res.partner'
      
    out_of_state=fields.Boolean(string="Out of state")
    state_code=fields.Char(string="State Code",required=True)
    gst_in=fields.Char(string="GSTIN")
    
class ResCompany(models.Model):
    _inherit ='res.company'
    state_code=fields.Char(string="State Code",required=True)
    gst_in=fields.Char(string="GSTIN")

class ProductCategoryInherit(models.Model):
    _inherit='product.category'
      
    
class ProductTemplateInherit(models.Model):
    _inherit= "product.template"
    
    hsn=fields.Char(string="HSN/SAC",related="product_variant_ids.hsn")
    
    @api.model
    def create(self, vals):
        
        product_template_id = super(ProductTemplateInherit, self).create(vals)
        
        related_vals = {}
        if vals.get('hsn'):
            related_vals['hsn'] = vals['hsn']
        product_template_id.update(related_vals)


        return product_template_id
     
class ProductProductInherit(models.Model):
    _inherit= "product.product"
    
    hsn=fields.Char(string="HSN/SAC")


class StockInherit(models.Model):
    _inherit = 'stock.picking'



    def _get_amount(self, amt):
        amt = amt
        amount_in_word = Number2Words().convertNumberToWords(amt)
        return amount_in_word


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    price_subtotal_tax = fields.Float(compute='_compute_price_tax', string='Taxable Value',
                                      digits=dp.get_precision('Product Price'), store=True)
    price_subtotal_taxinc = fields.Float(compute='_compute_price_tax', string=' Total',
                                      digits=dp.get_precision('Product Price'), store=True)

    price_unit_tax = fields.Float(compute='_compute_price_tax', string='Unit Price(Exc)',
                                  digits=dp.get_precision('Product Price'), store=True)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price_tax(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        prec = currency.decimal_places
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        q = 1
        unit_taxes = self.invoice_line_tax_ids.compute_all(price, currency, q, product=self.product_id,
                                                           partner=self.invoice_id.partner_id)
        taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                      partner=self.invoice_id.partner_id)
        self.price_unit_tax = unit_taxes['total_excluded']
        self.price_subtotal_tax = taxes['total_excluded']
        self.price_subtotal_taxinc =taxes['total_included']
        if self.invoice_id:
            self.price_subtotal_tax = round(self.price_subtotal_tax, prec)
            self.price_subtotal_taxinc = round(self.price_subtotal_taxinc, prec)
            self.price_unit_tax = self.invoice_id.currency_id.round(self.price_unit_tax)