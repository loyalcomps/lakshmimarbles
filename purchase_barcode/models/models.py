# -*- coding: utf-8 -*-

from odoo import models, fields, api,SUPERUSER_ID
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

# class purchase_barcode(models.Model):
#     _inherit = 'purchase.order'
#
#     barcode = fields.Char(string="Barcode")
#
#     @api.onchange('barcode')
#     def onchange_barcode_load_product(self):
#         if not self.barcode:
#             return {}
#
#         result = {}
#         values = {}
#         order_line_var = self.env['purchase.order.line']
#         product = self.env['product.product'].search([('barcode', '=', self.barcode)])
#         if not product:
#             self.barcode = False
#
#             return {
#
#                 'warning': {'title': 'Error!', 'message': 'Please enter the correct barcode'},
#                 'value': {
#                     'barcode': False,
#
#                 }
#             }
#         for prd in product:
#
#             values={
#                 'price_unit': 0.0,
#                 'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
#
#                 'product_id':prd.id,
#                 'product_uom':prd.uom_id,
#                 'hsn':prd.hsn,
#                 'product_mrp':prd.product_mrp,
#                 'barcode':prd.barcode,
#                 'brand_id':prd.brand_id,
#                 'category_id':prd.categ_id
#             }
#
#             product_lang = prd.with_context({
#                 'lang': self.partner_id.lang,
#                 'partner_id': self.partner_id.id,
#             })
#
#             values['name'] = product_lang.display_name
#             if product_lang.description_purchase:
#                 values['name'] += '\n' + product_lang.description_purchase
#
#             fpos = self.fiscal_position_id
#             if self.env.uid == SUPERUSER_ID:
#                 company_id = self.env.user.company_id.id
#                 values['taxes_id'] = fpos.map_tax(
#                     prd.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
#             else:
#                 values['taxes_id'] = fpos.map_tax(prd.supplier_taxes_id)
#
#             seller_min_qty = prd.seller_ids \
#                 .filtered(lambda r: r.name == self.partner_id) \
#                 .sorted(key=lambda r: r.min_qty)
#             if seller_min_qty:
#                 values['product_qty'] = seller_min_qty[0].min_qty or 1.0
#                 values['product_uom'] = seller_min_qty[0].product_uom
#             else:
#                 values['product_qty'] = 1.0
#
#             seller = prd._select_seller(
#                 partner_id=self.partner_id,
#                 quantity=values['product_qty'],
#                 date=self.date_order and self.date_order[:10],
#                 uom_id=values['product_uom'])
#
#
#             price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price,
#                                                                                  prd.supplier_taxes_id,
#                                                                                  values['taxes_id'],
#                                                                                  self.company_id) if seller else 0.0
#             if price_unit and seller and self.currency_id and seller.currency_id != self.currency_id:
#                 price_unit = seller.currency_id.compute(price_unit, self.currency_id)
#
#             if seller and values['product_uom'] and seller.product_uom != values['product_uom']:
#                 price_unit = values['product_uom']._compute_price(price_unit, values['product_uom'])
#
#             values['price_unit'] = price_unit
#
#             order_line_var1 = order_line_var.new(values)
#             order_line_var += order_line_var1
#
#
#         self.order_line += order_line_var
#         self.barcode = False
#         return

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_bool = fields.Boolean('Product',default='_product_invoice_checking_status')
    barcode_scan = fields.Char(string='Product Barcode', help="Here you can provide the barcode for the product")
    multi_barcode = fields.Many2one('product.barcode',string="multi Barcode",)
    product_tmpl_id = fields.Many2one('product.template',string="Product Template",related='product_id.product_tmpl_id', store=True,)


    @api.multi
    @api.onchange('multi_barcode')
    def _product_invoice_checking_status(self):

        for line in self:
            if not line.multi_barcode:
                line.product_bool = False
            if line.multi_barcode:
                line.product_bool = True

    @api.onchange('barcode_scan','product_id')
    def _onchange_barcode_scan(self):
        product_rec = self.env['product.product']
        product_ids = []
        result = {}
        if self.barcode_scan:
            product = product_rec.search([('barcode', '=', self.barcode_scan)])
            if product:
                product_ids.append(product.id)


            product_tmpl_ids = self.env['product.barcode'].search([('barcode','=',self.barcode_scan)])

            for product_tmpl in product_tmpl_ids:
                product = product_rec.search([('product_tmpl_id', '=', product_tmpl.product_tmpl_id.id)])
                product_ids.append(product.id)
            # if len(product_ids) == 1:
            #     self.product_id = product_ids[0]
            # else:
            result['domain'] = {'product_id': [('id', 'in', product_ids)]}

            return result
        else:
            products=self.env['product.product'].search([]).ids
            result['domain'] = {'product_id': [('id', 'in', products)]}

            return result

    # @api.onchange('product_id')
    # def load_multibarcode(self):
    #     res = {}
    #     if self.product_id:
    #         res['domain'] = {'multi_barcode': [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)]}
    #
    #     return res

    @api.onchange('multi_barcode')
    def load_multibarcode_product(self):
        if self.multi_barcode:
            self.product_mrp = self.multi_barcode.product_mrp
            self.sale_price = self.multi_barcode.list_price

        else:
            self.product_mrp = self.product_id.product_mrp
            self.sale_price = self.product_id.lst_price



        # if self.barcode_scan:
        #     if self.barcode_scan == self.product_id.barcode:
        #         self.product_mrp = self.product_id.product_mrp
        #     else:
        #         product = self.env['product.barcode'].search([('barcode', '=', self.barcode_scan),
        #                                             ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)],limit=1)
        #         self.product_mrp = product.product_mrp

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
                        # for record in product:
                        #     record.product_mrp = vals['product_mrp']
                    if 'sale_price' in vals:
                        product.list_price = vals['sale_price']
                        # for record in product:
                        #     record.list_price = vals['sale_price']
            else:
                if 'product_mrp' in vals:
                    product_id.product_mrp = vals['product_mrp']
                if 'sale_price' in vals:
                    product_id.lst_price = vals['sale_price']
            # else:
            #     if 'product_mrp' in vals:
            #         product_id.product_mrp = vals['product_mrp']
            #     if 'sale_price' in vals:
            #         product_id.lst_price = vals['sale_price']
            # if 'barcode_scan' in vals:
            #     if vals['barcode_scan'] == product_id.barcode:
            #         if 'product_mrp' in vals:
            #             product_id.product_mrp = vals['product_mrp']
            #     else:
            #         product = self.env['product.barcode'].search([('barcode', '=', vals['barcode_scan']),
            #                                                       ('product_tmpl_id', '=',
            #                                                        product_id.product_tmpl_id.id)], limit=1)
            #         if 'product_mrp' in vals:
            #             product.product_mrp = vals['product_mrp']
            # else:
            #     if 'product_mrp' in vals:
            #         product_id.product_mrp = vals['product_mrp']



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
                    if 'sale_price' in vals:
                        # product.list_price = vals['sale_price']
                        for record in product:
                            record.list_price = vals['sale_price']

                        # product.product_mrp = vals['product_mrp']
            elif self.multi_barcode and self.product_bool ==True:
                product = self.env['product.barcode'].search([('id', '=', self.multi_barcode.id),
                                                              ('product_tmpl_id', '=',
                                                               product_id.product_tmpl_id.id)])
                if 'product_mrp' in vals:
                    for record in product:
                            record.product_mrp = vals['product_mrp']
                    # product.product_mrp = vals['product_mrp']
                if 'sale_price' in vals:
                    # product.list_price = vals['sale_price']
                    for record in product:
                        record.list_price = vals['sale_price']

            else:
                if 'product_mrp' in vals:
                    product_id.product_mrp = vals['product_mrp']
                if 'sale_price' in vals:
                    product_id.lst_price = vals['sale_price']
            # if 'barcode_scan' in vals:
            #     if vals['barcode_scan'] == product_id.barcode:
            #         if 'product_mrp' in vals:
            #             product_id.product_mrp = vals['product_mrp']
            #     else:
            #         product = self.env['product.barcode'].search([('barcode', '=', vals['barcode_scan']),
            #                                                       ('product_tmpl_id', '=',
            #                                                        product_id.product_tmpl_id.id)], limit=1)
            #         if 'product_mrp' in vals:
            #             product.product_mrp = vals['product_mrp']
            # else:
            #     if self.barcode_scan:
            #         if self.barcode_scan == product_id.barcode:
            #             if 'product_mrp' in vals:
            #                 product_id.product_mrp = vals['product_mrp']
            #         else:
            #             product = self.env['product.barcode'].search([('barcode', '=', self.barcode_scan),
            #                                                       ('product_tmpl_id', '=',
            #                                                        product_id.product_tmpl_id.id)], limit=1)
            #             if 'product_mrp' in vals:
            #                 product.product_mrp = vals['product_mrp']
            #     else:
            #         if 'product_mrp' in vals:
            #             product_id.product_mrp = vals['product_mrp']


        return super(PurchaseOrderLine, self).write(vals)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    invproduct_bool = fields.Boolean('Product',default='_product_invoice_checking')


    barcode_scan = fields.Char(string='Product Barcode', help="Here you can provide the barcode for the product")
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







#     @api.onchange('product_id')
#     def _onchange_product_id(self):
#         res = super(AccountInvoiceLine, self)._onchange_product_id()
#
#         if self.barcode_scan:
#             if self.barcode_scan == self.product_id.barcode:
#                 self.product_mrp = self.product_id.product_mrp
#                 self.sale_price = self.product_id.lst_price
#             else:
#                 product = self.env['product.barcode'].search([('barcode', '=', self.barcode_scan),
#                                                     ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)],limit=1)
#                 self.product_mrp = product.product_mrp
#                 self.sale_price = product.list_price

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
                        # product.product_mrp = vals['product_mrp']
                        for record in product:
                            record.product_mrp = vals['product_mrp']
                    if 'sale_price' in vals:
                        # product.list_price = vals['sale_price']
                        for record in product:
                            record.list_price = vals['sale_price']
                elif self.multi_barcodes:
                    product = self.env['product.barcode'].search([('id', '=', self.multi_barcodes.id),
                                                                  ('product_tmpl_id', '=',
                                                                   product_id.product_tmpl_id.id)])
                    if 'product_mrp' in vals:
                        for record in product:
                            record.product_mrp = vals['product_mrp']
                        # product.product_mrp = vals['product_mrp']
                    if 'sale_price' in vals:
                        for record in product:
                            record.list_price = vals['sale_price']
            else:
                if 'product_mrp' in vals:
                    product_id.product_mrp = vals['product_mrp']
                if 'sale_price' in vals:
                    product_id.lst_price = vals['sale_price']
            # else:
            #     if 'product_mrp' in vals:
            #         product_id.product_mrp = vals['product_mrp']
            #     if 'sale_price' in vals:
            #         product_id.lst_price = vals['sale_price']
            # if 'barcode_scan' in vals:
            #     if vals['barcode_scan'] == product_id.barcode:
            #         if 'product_mrp' in vals:
            #             product_id.product_mrp = vals['product_mrp']
            #         if 'sale_price' in vals:
            #             product_id.lst_price = vals['sale_price']
            #     else:
            #         product = self.env['product.barcode'].search([('barcode', '=', vals['barcode_scan']),
            #                                                       ('product_tmpl_id', '=',
            #                                                        product_id.product_tmpl_id.id)], limit=1)
            #         if 'product_mrp' in vals:
            #             product.product_mrp = vals['product_mrp']
            #         if 'sale_price' in vals:
            #             product.list_price = vals['sale_price']
            # else:
            #     if 'product_mrp' in vals:
            #         product_id.product_mrp = vals['product_mrp']
            #     if 'sale_price' in vals:
            #         product_id.lst_price = vals['sale_price']



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
                        # product.product_mrp = vals['product_mrp']
                    if 'sale_price' in vals:
                        # product.list_price = vals['sale_price']
                        for record in product:
                            record.list_price = vals['sale_price']
            elif self.multi_barcodes:
                product = self.env['product.barcode'].search([('id', '=', self.multi_barcodes.id),
                                                              ('product_tmpl_id', '=',
                                                               product_id.product_tmpl_id.id)])
                if 'product_mrp' in vals:
                    for record in product:
                        record.product_mrp = vals['product_mrp']
                    # product.product_mrp = vals['product_mrp']
                if 'sale_price' in vals:
                    for record in product:
                        record.list_price = vals['sale_price']
                    # product.list_price = vals['sale_price']
            else:
                if 'product_mrp' in vals:
                    product_id.product_mrp = vals['product_mrp']
                if 'sale_price' in vals:
                    product_id.lst_price = vals['sale_price']

            # if 'barcode_scan' in vals:
            #     if vals['barcode_scan'] == product_id.barcode:
            #         if 'product_mrp' in vals:
            #             product_id.product_mrp = vals['product_mrp']
            #         if 'sale_price' in vals:
            #             product_id.lst_price = vals['sale_price']
            #     else:
            #         product = self.env['product.barcode'].search([('barcode', '=', vals['barcode_scan']),
            #                                                       ('product_tmpl_id', '=',
            #                                                        product_id.product_tmpl_id.id)], limit=1)
            #         if 'product_mrp' in vals:
            #             product.product_mrp = vals['product_mrp']
            #         if 'sale_price' in vals:
            #             product.list_price = vals['sale_price']
            # else:
            #     if self.barcode_scan:
            #         if self.barcode_scan == product_id.barcode:
            #             if 'product_mrp' in vals:
            #                 product_id.product_mrp = vals['product_mrp']
            #             if 'sale_price' in vals:
            #                 product_id.lst_price = vals['sale_price']
            #         else:
            #             product = self.env['product.barcode'].search([('barcode', '=', self.barcode_scan),
            #                                                       ('product_tmpl_id', '=',
            #                                                        product_id.product_tmpl_id.id)], limit=1)
            #             if 'product_mrp' in vals:
            #                 product.product_mrp = vals['product_mrp']
            #             if 'sale_price' in vals:
            #                 product.list_price = vals['sale_price']
            #     else:
            #         if 'product_mrp' in vals:
            #             product_id.product_mrp = vals['product_mrp']
            #         if 'sale_price' in vals:
            #             product_id.lst_price = vals['sale_price']


        return super(AccountInvoiceLine, self).write(vals)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        var = {}

        for l in line:
            product_mrp = l.product_id.product_mrp
            sale_price = l.product_id.lst_price
            if l.multi_barcode:
                sale_price = l.multi_barcode.list_price
                product_mrp = l.multi_barcode.product_mrp

            var = {
                    'barcode_scan': l.barcode_scan,
                    'multi_barcodes': l.multi_barcode.id,
                    'sale_price': sale_price,
                    'product_mrp': product_mrp,
                    'invproduct_bool':l.product_bool,
            }
            # if l.barcode_scan:
            #     if l.barcode_scan == l.product_id.barcode:
            #         var = {
            #             'barcode_scan': l.barcode_scan,
            #             'multi_barcode': l.multi_barcode,
            #             # 'sale_price': l.product_id.lst_price,
            #         }
            #     else:
            #         product = self.env['product.barcode'].search([('barcode', '=', l.barcode_scan),
            #                                                       ('product_tmpl_id', '=',
            #                                                        l.product_id.product_tmpl_id.id)], limit=1)
            #         var = {
            #             'barcode_scan': l.barcode_scan,
            #             # 'sale_price': product.list_price
            #         }

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


