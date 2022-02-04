# -*- coding: utf-8 -*-

from odoo import models, fields, api,SUPERUSER_ID
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    barcode = fields.Char(string="Barcode")

    @api.onchange('barcode')
    def onchange_barcode_load_product(self):
        if not self.barcode:
            return {}

        product_ids = []
        product = self.env['product.product'].search([('barcode', '=', self.barcode)])

        if product:
            product_ids.append(product.id)
        product_tmpl_ids = self.env['product.barcode'].search([('barcode', '=', self.barcode)])

        for product_tmpl in product_tmpl_ids:
            product = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl.product_tmpl_id.id)])
            if product.id not in product_ids:
                product_ids.append(product.id)
        if not product_ids:
            self.barcode = False

            return {

                'warning': {'title': 'Error!', 'message': 'Please enter the correct barcode'},
                'value': {
                    'barcode': False,

                }
            }
        if len(product_ids)==1:


            for prd in product:

                product_lang = prd.with_context({
                    'lang': self.partner_id.lang,
                    'partner_id': self.partner_id.id,
                })
                name = product_lang.display_name
                if product_lang.description_purchase:
                    name += '\n' + product_lang.description_purchase

                fpos = self.fiscal_position_id
                if self.env.uid == SUPERUSER_ID:
                    company_id = self.env.user.company_id.id
                    taxes_id = fpos.map_tax(
                        prd.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
                else:
                    taxes_id = fpos.map_tax(prd.supplier_taxes_id)

                order_line_var = self.env['purchase.order.line']
                values = {
                    'product_id': prd.id,
                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'product_uom': prd.uom_po_id or prd.uom_id,
                    'name': name,
                    'taxes_id': taxes_id,
                    'barcode': prd.barcode,
                    'hsn': prd.hsn,
                    'product_article_no': prd.id,
                    'product_mrp': prd.product_mrp,
                    'sale_price': prd.lst_price
                }

                order_line_var1 = order_line_var.new(values)
                order_line_var1._suggest_quantity()
                order_line_var1._onchange_quantity()
                order_line_var += order_line_var1
                self.order_line += order_line_var
                self.barcode = False

            self.barcode = False


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_bool = fields.Boolean('Product',default='_product_invoice_checking_status')
    # barcode_scan = fields.Char(string='Product Barcode', help="Here you can provide the barcode for the product")
    multi_barcode = fields.Many2one('product.barcode',string="Multi Barcode",)
    product_tmpl_id = fields.Many2one('product.template',string="Product Template",related='product_id.product_tmpl_id', store=True,)

    # @api.onchange('product_id')
    # def barcode_scan_domain(self):
    #     product_rec = self.env['product.product']
    #     product_ids=[]
    #     result={}
    #     if self._context.get('scan_barcode'):
    #         barcode_scan=self._context.get('scan_barcode')
    #         product = product_rec.search([('barcode', '=', barcode_scan)])
    #         if product:
    #             product_ids.append(product.id)
    #
    #         product_tmpl_ids = self.env['product.barcode'].search([('barcode', '=', barcode_scan)])
    #
    #         for product_tmpl in product_tmpl_ids:
    #             product = product_rec.search([('product_tmpl_id', '=', product_tmpl.product_tmpl_id.id)])
    #             product_ids.append(product.id)
    #
    #         self.order_id.barcode=False
    #         result['domain'] = {'product_id': [('id', 'in', product_ids)]}
    #
    #         return result


    @api.multi
    @api.onchange('multi_barcode')
    def _product_invoice_checking_status(self):

        for line in self:
            if not line.multi_barcode:
                line.product_bool = False
            if line.multi_barcode:
                line.product_bool = True

    # @api.onchange('barcode_scan','product_id')
    # def _onchange_barcode_scan(self):
    #     product_rec = self.env['product.product']
    #     product_ids = []
    #     result = {}
    #     if self.barcode_scan:
    #         product = product_rec.search([('barcode', '=', self.barcode_scan)])
    #         if product:
    #             product_ids.append(product.id)
    #
    #
    #         product_tmpl_ids = self.env['product.barcode'].search([('barcode','=',self.barcode_scan)])
    #
    #         for product_tmpl in product_tmpl_ids:
    #             product = product_rec.search([('product_tmpl_id', '=', product_tmpl.product_tmpl_id.id)])
    #             product_ids.append(product.id)
    #
    #         result['domain'] = {'product_id': [('id', 'in', product_ids)]}
    #
    #         return result
    #     else:
    #         products=self.env['product.product'].search([]).ids
    #         result['domain'] = {'product_id': [('id', 'in', products)]}
    #
    #         return result


    @api.onchange('multi_barcode')
    def load_multibarcode_product(self):
        if self.multi_barcode:
            self.product_mrp = self.multi_barcode.product_mrp
            self.sale_price = self.multi_barcode.list_price

        else:
            self.product_mrp = self.product_id.product_mrp
            self.sale_price = self.product_id.lst_price




    @api.model
    def create(self, vals):

        if vals['product_id']:

            product_id = self.env['product.product'].search([('id', '=', vals['product_id'])])
            if 'multi_barcode' in vals:
                if vals['multi_barcode']:
                    product = self.env['product.barcode'].search([('id', '=', vals['multi_barcode']),
                                                              ('product_tmpl_id', '=',
                                                               product_id.product_tmpl_id.id)])
                    if 'product_mrp' in vals:
                        product.product_mrp = vals['product_mrp']

                    # if 'sale_price' in vals:
                    #     product.list_price = vals['sale_price']

            else:
                if 'product_mrp' in vals:
                    product_id.product_mrp = vals['product_mrp']
                # if 'sale_price' in vals:
                #     product_id.lst_price = vals['sale_price']

        return super(PurchaseOrderLine, self).create(vals)

    @api.multi
    def write(self, vals):

        if self.product_id:
            product_id = self.env['product.product'].search([('id', '=', self.product_id.id)])

            if 'multi_barcode' in vals:
                if vals['multi_barcode']:
                    product = self.env['product.barcode'].search([('id', '=', vals['multi_barcode']),
                                                              ('product_tmpl_id', '=',
                                                               product_id.product_tmpl_id.id)])
                    if 'product_mrp' in vals:
                        for record in product:
                            record.product_mrp = vals['product_mrp']
                    # if 'sale_price' in vals:
                    #
                    #     for record in product:
                    #         record.list_price = vals['sale_price']

            elif self.multi_barcode and self.product_bool ==True:
                product = self.env['product.barcode'].search([('id', '=', self.multi_barcode.id),
                                                              ('product_tmpl_id', '=',
                                                               product_id.product_tmpl_id.id)])
                if 'product_mrp' in vals:
                    for record in product:
                            record.product_mrp = vals['product_mrp']

                # if 'sale_price' in vals:
                #
                #     for record in product:
                #         record.list_price = vals['sale_price']

            else:
                if 'product_mrp' in vals:
                    product_id.product_mrp = vals['product_mrp']
                # if 'sale_price' in vals:
                #     product_id.lst_price = vals['sale_price']

        return super(PurchaseOrderLine, self).write(vals)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    invproduct_bool = fields.Boolean('Product',default='_product_invoice_checking')


    # barcode_scan = fields.Char(string='Product Barcode', help="Here you can provide the barcode for the product")
    multi_barcodes = fields.Many2one('product.barcode', string="multi Barcode", )
    product_tmpl_id = fields.Many2one('product.template',string="Product Template",related='product_id.product_tmpl_id', store=True,)

    @api.multi
    @api.onchange('multi_barcodes')
    def _product_invoice_checking(self):

        for line in self:
            if not line.multi_barcodes:
                line.invproduct_bool = False
            if line.multi_barcodes:
                line.invproduct_bool = True


    @api.onchange('multi_barcodes')
    def load_invoice_product(self):
        if self.multi_barcodes:
            self.product_mrp = self.multi_barcodes.product_mrp
            self.sale_price = self.multi_barcodes.list_price

        else:
            self.product_mrp = self.product_id.product_mrp
            self.sale_price = self.product_id.lst_price

    #
    @api.model
    def create(self, vals):

        if vals['product_id']:

            product_id = self.env['product.product'].search([('id', '=', vals['product_id'])])

            if not product_id:
                return super(AccountInvoiceLine, self).create(vals)
            if 'multi_barcodes' in vals:
                if vals['multi_barcodes']:
                    product = self.env['product.barcode'].search([('id', '=', vals['multi_barcodes']),
                                                              ('product_tmpl_id', '=',
                                                               product_id.product_tmpl_id.id)])

                    if 'product_mrp' in vals:

                        for record in product:
                            record.product_mrp = vals['product_mrp']
                    # if 'sale_price' in vals:
                    #
                    #     for record in product:
                    #         record.list_price = vals['sale_price']
                elif self.multi_barcodes:
                    product = self.env['product.barcode'].search([('id', '=', self.multi_barcodes.id),
                                                                  ('product_tmpl_id', '=',
                                                                   product_id.product_tmpl_id.id)])
                    if 'product_mrp' in vals:
                        for record in product:
                            record.product_mrp = vals['product_mrp']

                    # if 'sale_price' in vals:
                    #     for record in product:
                    #         record.list_price = vals['sale_price']
            else:
                if 'product_mrp' in vals:
                    product_id.product_mrp = vals['product_mrp']
                # if 'sale_price' in vals:
                #     product_id.lst_price = vals['sale_price']

        return super(AccountInvoiceLine, self).create(vals)

    @api.multi
    def write(self, vals):

        if self.product_id:
            product_id = self.env['product.product'].search([('id', '=', self.product_id.id)])
            if 'multi_barcodes' in vals:
                if vals['multi_barcodes']:
                    product = self.env['product.barcode'].search([('id', '=', vals['multi_barcodes']),
                                                              ('product_tmpl_id', '=',
                                                               product_id.product_tmpl_id.id)])
                    if 'product_mrp' in vals:
                        for record in product:
                            record.product_mrp = vals['product_mrp']

                    # if 'sale_price' in vals:
                    #
                    #     for record in product:
                    #         record.list_price = vals['sale_price']
            elif self.multi_barcodes:
                product = self.env['product.barcode'].search([('id', '=', self.multi_barcodes.id),
                                                              ('product_tmpl_id', '=',
                                                               product_id.product_tmpl_id.id)])
                if 'product_mrp' in vals:
                    for record in product:
                        record.product_mrp = vals['product_mrp']

                # if 'sale_price' in vals:
                #     for record in product:
                #         record.list_price = vals['sale_price']

            else:
                if 'product_mrp' in vals:
                    product_id.product_mrp = vals['product_mrp']
                # if 'sale_price' in vals:
                #     product_id.lst_price = vals['sale_price']


        return super(AccountInvoiceLine, self).write(vals)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        var = {}

        for l in line:
            sale_price = l.product_id.lst_price
            if l.multi_barcode:
                sale_price = l.multi_barcode.list_price

            var = {
                    # 'barcode_scan': l.barcode_scan,
                    'multi_barcodes': l.multi_barcode.id,
                    'sale_price': sale_price,
                    'invproduct_bool':l.product_bool,
            }

        res.update(var)
        return res

class product_barcode(models.Model):
    _inherit = 'product.barcode'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.barcode + ' ' + '[' + str(record.product_mrp) + ']'+ ' ' + '[' + str(record.list_price) + ']'
            result.append((record.id, name))
        return result


