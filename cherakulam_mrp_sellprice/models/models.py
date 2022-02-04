# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Cherakulam_mrp_sellprice(models.Model):
    _inherit = 'purchase.order.line'

    product_mrp = fields.Float(string="MRP", )

    sale_price = fields.Float(string="Sale Price", default=0.0)

    # customer_tax_id = fields.Many2many('account.tax', string='Customer Taxes', required=True,
    #                                    domain=['|', ('active', '=', False), ('active', '=', True)])

    @api.model
    def create(self, vals):

        if vals['product_id']:

            product_id = self.env['product.product'].search([('id', '=', vals['product_id'])])

            if not product_id:
                return super(Cherakulam_mrp_sellprice, self).create(vals)


            # if 'customer_tax_id' in vals:
            #     product_id.taxes_id = vals['customer_tax_id']

            if 'product_mrp' in vals:
                product_id.product_mrp = vals['product_mrp']

            if 'sale_price' in vals:
                product_id.lst_price = vals['sale_price']


        return super(Cherakulam_mrp_sellprice, self).create(vals)

    @api.multi
    def write(self, vals):

        if self.product_id:
            product_id = self.env['product.product'].search([('id', '=', self.product_id.id)])

            # if 'customer_tax_id' in vals:
            #     product_id.taxes_id = vals['customer_tax_id']
            if 'product_mrp' in vals:
                product_id.product_mrp = vals['product_mrp']

            if 'sale_price' in vals:
                product_id.lst_price = vals['sale_price']

        return super(Cherakulam_mrp_sellprice, self).write(vals)

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(Cherakulam_mrp_sellprice, self).onchange_product_id()

        # self.customer_tax_id = self.product_id.taxes_id
        self.product_mrp = self.product_id.product_mrp

        self.sale_price = self.product_id.lst_price

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):

        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        for l in line:
            var = {


                # 'customer_tax_id': l.product_id.taxes_id,
                'product_mrp':l.product_mrp,
                'sale_price': l.product_id.lst_price,

            }
        res.update(var)
        return res

class CherakulamAccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    sale_price = fields.Float(string="Sale Price", default=0.0)

    # product_mrp = fields.Float(string="MRP", )

    @api.model
    def create(self, vals):

        if vals['product_id']:

            product_id = self.env['product.product'].search([('id', '=', vals['product_id'])])

            if not product_id:
                return super(CherakulamAccountInvoiceLine, self).create(vals)


            # if 'product_mrp' in vals:
            #     product_id.product_mrp = vals['product_mrp']

            if 'sale_price' in vals:
                product_id.lst_price = vals['sale_price']


        return super(CherakulamAccountInvoiceLine, self).create(vals)

    @api.multi
    def write(self, vals):

        if self.product_id:
            product_id = self.env['product.product'].search([('id', '=', self.product_id.id)])

            # if 'product_mrp' in vals:
            #     product_id.product_mrp = vals['product_mrp']
            #
            if 'sale_price' in vals:
                product_id.lst_price = vals['sale_price']


        return super(CherakulamAccountInvoiceLine, self).write(vals)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(CherakulamAccountInvoiceLine, self)._onchange_product_id()


        # self.product_mrp = self.product_id.product_mrp

        self.sale_price = self.product_id.lst_price











