# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('partner_id',)
    def _get_refund_invoice(self):
        for record in self:
            if record.type in ('out_invoice','in_invoice'):
                return
            record.refund_invoice_id = False
            type = 'out_invoice' if record.type=='out_refund' else 'in_invoice'
            if not record.partner_id:
                return {'domain': {'refund_invoice_id': [('type', '=', type),('state','in',('open','paid'))]}}
            domain = {'refund_invoice_id': [('type', '=', type),('state','in',('open','paid')),('partner_id', '=', record.partner_id.id)]}
            result = {'domain': domain}
            return result

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


    @api.onchange('product_id')
    def onchange_product_id_get_domain(self):
        productid_list = []
        if not self._context.get('refund_invoice_id'):
            return
        if self._context.get('refund_invoice_id'):
            invoiceline_id = self.env["account.invoice.line"].search([('invoice_id','=',self._context.get('refund_invoice_id'))])
            for line_id in invoiceline_id:
                productid_list.append(line_id.product_id.id)
            result = {'domain': {'product_id': [('id', 'in', productid_list)]}}
            return result

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.invoice_id.type in ('out_refund','in_refund') and self.invoice_id.refund_invoice_id and self.product_id:
            dct ={
                'quantity':0,
                'price_unit':0,
            }
            s=0

            for line in self.invoice_id.refund_invoice_id.invoice_line_ids.filtered(lambda t: t.product_id.id == self.product_id.id):
                dct['quantity']+= line.quantity
                if s==0:
                    dct['price_unit'] = line.price_unit
                    s+=1
                dct['uom_id']=line.uom_id.id
            self.update(dct)

    @api.constrains('quantity','price_unit')
    def check_quantity(self):
        for record in self:
            if record.invoice_id.type in (
            'out_refund', 'in_refund') and record.invoice_id.refund_invoice_id and record.product_id:
                quantity = 0
                price_unit =0
                s = 0
                for line in self.invoice_id.refund_invoice_id.invoice_line_ids.filtered(
                        lambda t: t.product_id.id == self.product_id.id):
                    quantity += line.quantity
                    if s==0:
                        price_unit = line.price_unit
                        s += 1

                if record.quantity > quantity:
                    raise ValidationError("%s's actual quantity is %s" % (record.product_id.name,quantity))
                if record.price_unit > price_unit or record.price_unit < price_unit:
                    raise ValidationError(
                        "%s's actual price is %s" % (record.product_id.name,price_unit))
#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100