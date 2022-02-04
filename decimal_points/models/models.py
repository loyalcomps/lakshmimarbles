# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class Purchaseorder(models.Model):
    _inherit = 'purchase.order'


    amount_untaxed = fields.Monetary(string='Untaxed Amount',digits=dp.get_precision('amount untaxed'))
    amount_tax = fields.Monetary(string='Taxes', digits=dp.get_precision('amount tax'))
    amount_total = fields.Monetary(string='Total', digits=dp.get_precision('amount total'))

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Purchase Unit Price'))
    discount_percentage = fields.Float(string="Discount(%)", default=0.0, digits=dp.get_precision('Purchase Discount Percentage'))
    discount_amount = fields.Float(string="Discount(amt)", default=0.0,digits=dp.get_precision('Purchase Discount amount'))


    price_subtotal = fields.Monetary(string='Subtotal',digits=dp.get_precision('price subtotal'))
    price_total = fields.Monetary( string='Total',digits=dp.get_precision('price total'))
    price_tax = fields.Monetary(string='Tax', digits=dp.get_precision('price tax'))




class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Purchase Unit Price'))

    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Account Discount Per'),
                            default=0.0)
    discount_amount = fields.Float(string="Discount(amt)", default=0.0,digits=dp.get_precision('Purchase Discount Per'))