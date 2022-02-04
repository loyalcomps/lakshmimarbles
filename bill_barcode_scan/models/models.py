# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    barcode_scan = fields.Char(string='Barcode', help="Here you can provide the barcode for the product")
    multi_barcode = fields.Many2one('product.barcode', string="Multi Barcode", )
    product_tmpl_id = fields.Many2one('product.template', string="Product Template",
                                      related='product_id.product_tmpl_id', store=True, )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()

        self.multi_barcode = False

    @api.onchange('barcode_scan', 'product_id')
    def _onchange_barcode_scan(self):
        product_rec = self.env['product.product']
        product_ids = []
        result = {}
        if self.barcode_scan:
            product = product_rec.search([('barcode', '=', self.barcode_scan)])
            if product:
                product_ids.append(product.id)

            product_tmpl_ids = self.env['product.barcode'].search([('barcode', '=', self.barcode_scan)])

            for product_tmpl in product_tmpl_ids:
                product = product_rec.search([('product_tmpl_id', '=', product_tmpl.product_tmpl_id.id)])
                product_ids.append(product.id)
            # if len(product_ids) == 1:
            #     self.product_id = product_ids[0]
            # else:
            result['domain'] = {'product_id': [('id', 'in', product_ids)]}

            return result
        else:
            products = self.env['product.product'].search([]).ids
            result['domain'] = {'product_id': [('id', 'in', products)]}

            return result

    @api.onchange('multi_barcode')
    def load_multibarcode_product(self):
        if self.multi_barcode:
            self.product_mrp = self.multi_barcode.product_mrp
            self.sell_price = self.multi_barcode.list_price
        else:
            self.product_mrp = self.product_id.product_mrp
            self.sell_price = self.product_id.list_price

    @api.model
    def create(self, values):
        line = super(AccountInvoiceLine, self).create(values)
        if line.multi_barcode:
            line.multi_barcode.list_price = line.sell_price
            line.multi_barcode.product_mrp = line.product_mrp
        else:
            line.product_id.list_price = line.sell_price
            line.product_id.product_mrp = line.product_mrp
        return line

    @api.multi
    def write(self, vals):
        sell = super(AccountInvoiceLine, self).write(vals)
        if 'multi_barcode' in vals and vals['multi_barcode']!=False:
            multi_barcode=self.env['product.barcode'].browse(vals['multi_barcode'])
            if 'sell_price' in vals:
                multi_barcode.list_price = vals['sell_price']
            if 'product_mrp' in vals:
                multi_barcode.product_mrp = vals['product_mrp']
        elif self.multi_barcode:
            if 'sell_price' in vals:
                self.multi_barcode.list_price = vals['sell_price']
            if 'product_mrp' in vals:
                self.multi_barcode.product_mrp = vals['product_mrp']
        else:
            if 'sell_price' in vals:
                self.product_id.list_price = vals['sell_price']
            if 'product_mrp' in vals:
                self.product_id.product_mrp = vals['product_mrp']
        return sell

class product_barcode(models.Model):
    _inherit = 'product.barcode'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.barcode + ' ' + '[' + str(record.product_mrp) + ']'+ ' ' + '[' + str(record.list_price) + ']'
            result.append((record.id, name))
        return result
