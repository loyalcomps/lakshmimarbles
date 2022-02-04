# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    margin = fields.Float('Margin',digits=dp.get_precision('Product Price'),related='product_variant_ids.margin',store=True)
    # margin_percentage = fields.Float('Margin (%)',default=0,related='product_variant_ids.margin_percentage')
    margin_discount_percentage = fields.Float('Margin Discount(%)',default=0,related='product_variant_ids.margin_discount_percentage',store=True)
    margin_sale_check = fields.Boolean('Check', default=True,related='product_variant_ids.margin_sale_check')


    # @api.depends('margin_discount_percentage', 'product_mrp', 'landing_cost')
    @api.onchange( 'product_mrp', 'landing_cost')
    def compute_margin(self):
        for record in self:
            if record.product_mrp :
                record.margin = record.product_mrp - record.landing_cost

    @api.onchange('margin_discount_percentage','margin')
    def compute_sale_price_using_margin(self):
        for record in self:
            if record.margin_sale_check == False:
                record.margin_sale_check = True
                return
            if record.product_mrp and record.margin_discount_percentage >0:
                # if record.list_price == record.product_mrp - ((record.margin * record.margin_discount_percentage) / 100):
                #     return
                record.list_price = record.product_mrp - ((record.margin * record.margin_discount_percentage) / 100)
                record.margin_sale_check = False
            if (not record.product_mrp) and record.margin_discount_percentage > 0:

                # if record.list_price == record.landing_cost + (
                #         (record.landing_cost * record.margin_discount_percentage) / 100):
                #     return
                record.list_price = record.landing_cost + (
                            (record.landing_cost * record.margin_discount_percentage) / 100)
                record.margin_sale_check = False


    @api.onchange('list_price','product_mrp','margin','landing_cost')
    def compute_margin_using_sale_price(self):
        for record in self:
            if record.margin_sale_check == False:
                record.margin_sale_check = True
                return
            if record.margin:
                # if record.margin_discount_percentage == ((record.product_mrp - record.list_price) / record.margin) * 100:
                #     return
                record.margin_discount_percentage = ((record.product_mrp - record.list_price) / record.margin) * 100

                record.margin_sale_check = False
            if (not record.product_mrp) and record.landing_cost != 0:

                # if record.margin_discount_percentage == ((record.list_price - record.landing_cost) / record.landing_cost) * 100:
                #     return
                record.margin_discount_percentage = ((record.list_price - record.landing_cost) / record.landing_cost) * 100
                record.margin_sale_check = False

    @api.model
    def create(self, vals):

        product_template_id = super(ProductTemplate, self).create(vals)
        related_vals = {}
        if vals.get('margin'):
            related_vals['margin'] = vals['margin']
        if vals.get('margin_discount_percentage'):
            related_vals['margin_discount_percentage'] = vals['margin_discount_percentage']
        # if vals.get('margin_percentage'):
        #     related_vals['margin_percentage'] = vals['margin_percentage']
        if related_vals:
            product_template_id.write(related_vals)

        return product_template_id
class ProductProduct(models.Model):
    _inherit = 'product.product'

    margin = fields.Float('Margin', digits=dp.get_precision('Product Price'),store=True)
    # margin_percentage = fields.Float('Margin (%)', default=0)
    margin_discount_percentage = fields.Float('Margin Discount(%)',default=0,store=True)
    margin_sale_check = fields.Boolean('Check',default=True)


    @api.onchange( 'product_mrp', 'landing_cost')
    def compute_margin(self):
        for record in self:
            
            if record.product_mrp:
                record.margin = record.product_mrp - record.landing_cost
            #     if record.margin_discount_percentage > 0:
            #
            #         record.lst_price = record.product_mrp - ((record.margin*record.margin_discount_percentage)/100)
            #
            # if not record.product_mrp and record.margin_discount_percentage > 0:
            #
            #     record.lst_price = record.landing_cost + ((record.landing_cost*record.margin_discount_percentage)/100)

    @api.onchange('margin_discount_percentage', 'margin')
    def compute_sale_price_using_margin(self):
        for record in self:
            if record.margin_sale_check == False:
                record.margin_sale_check = True
                return
            if record.product_mrp and record.margin_discount_percentage > 0:
                # record.margin_discount_percentage_dummy = record.margin_discount_percentage
                # record.list_price_dummy = record.product_mrp - (
                #         (record.margin * record.margin_discount_percentage) / 100)
                # if record.list_price_dummy == record.lst_price:
                # if record.lst_price == record.product_mrp - (
                #         (record.margin * record.margin_discount_percentage) / 100):
                #     return
                record.lst_price = record.product_mrp - (
                    (record.margin * record.margin_discount_percentage) / 100)
                record.margin_sale_check = False

            if (not record.product_mrp) and record.margin_discount_percentage > 0:
                # record.margin_discount_percentage_dummy = record.margin_discount_percentage
                # record.list_price_dummy = record.landing_cost + (
                #     (record.landing_cost * record.margin_discount_percentage) / 100)
                # if record.list_price_dummy == record.lst_price:
                # if record.lst_price == record.landing_cost + (
                #     (record.landing_cost * record.margin_discount_percentage) / 100):
                #     return
                record.lst_price = record.landing_cost + (
                    (record.landing_cost * record.margin_discount_percentage) / 100)
                record.margin_sale_check = False


    @api.onchange('lst_price','product_mrp','margin','landing_cost')
    def compute_margin_using_sale_price(self):
        for record in self:
            if record.margin_sale_check == False:
                record.margin_sale_check = True
                return
            if record.margin:
                # record.list_price_dummy = record.lst_price
                # record.margin_discount_percentage_dummy = ((record.product_mrp - record.lst_price) / record.margin) * 100
                # if record.margin_discount_percentage_dummy == record.margin_discount_percentage:
                # if record.margin_discount_percentage == ((record.product_mrp - record.lst_price) / record.margin) * 100:
                #     return
                record.margin_discount_percentage = ((record.product_mrp-record.lst_price)/record.margin)*100
                record.margin_sale_check = False

            if (not record.product_mrp) and record.landing_cost != 0:
                # record.list_price_dummy = record.lst_price
                # record.margin_discount_percentage_dummy = ((record.lst_price - record.landing_cost) / record.landing_cost) * 100
                # if record.margin_discount_percentage_dummy == record.margin_discount_percentage:
                # if record.margin_discount_percentage == ((record.lst_price - record.landing_cost) / record.landing_cost) * 100:
                #     return
                record.margin_discount_percentage = ((record.lst_price - record.landing_cost) / record.landing_cost) * 100
                record.margin_sale_check = False


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):

        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        for l in line:
            var = {
                'margin': l.product_id.margin,
                # 'margin_percentage':l.product_id.margin_percentage,
                # 'product_margin':l.product_id.margin,
                'margin_discount_percentage': l.product_id.margin_discount_percentage,


            }
        res.update(var)
        return res


    @api.multi
    def action_invoice_open(self):
        super(AccountInvoice, self).action_invoice_open()
        margin_discount_percentage = 0

        for record in self:
            if record.type == 'in_invoice':

                for line in record.invoice_line_ids:
                    line.product_id.margin = line.margin
                    if line.margin:
                        margin_discount_percentage = ((line.product_mrp - line.sale_price) / line.margin) * 100

                    if (not line.product_mrp) and line.landing_cost != 0:

                        margin_discount_percentage = ((line.sale_price - line.landing_cost) / line.landing_cost) * 100
                    line.product_id.margin_discount_percentage = margin_discount_percentage




class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    margin_sale_check = fields.Boolean('Check', default=True)

    @api.depends('landing_cost','product_mrp')
    def ComputeMargin(self):
        for line in self:
            if line.product_mrp:
                line.margin = line.product_mrp - line.landing_cost
                # line.product_id.margin = line.margin
                # if line.margin_discount_percentage > 0:
                #     line.sale_price = line.product_mrp - ((line.margin * line.margin_discount_percentage) / 100)

            # if not line.product_mrp:
                # if line.margin_discount_percentage > 0:
                #     line.sale_price = line.landing_cost + ((line.landing_cost * line.margin_discount_percentage) / 100)



    margin = fields.Float(string="Margin", compute="ComputeMargin", store=True,default=0)
    # margin_percentage = fields.Float(string="Margin(%)", default=0,compute="ComputeMargin", store=True)
    # product_margin = fields.Float(string="Product Margin",default=0)
    margin_discount_percentage = fields.Float('Margin Discount(%)', default=0)

    # @api.onchange('margin', 'margin_discount_percentage')
    # def ComputeSalePriceMargin(self):
    #     for line in self:
    #         if line.margin_sale_check == False:
    #             line.margin_sale_check = True
    #             return
    #         if line.product_mrp:
    #
    #             if line.margin_discount_percentage > 0:
    #                 line.sale_price = line.product_mrp - ((line.margin * line.margin_discount_percentage) / 100)
    #                 line.margin_sale_check = False
    #         if not line.product_mrp:
    #             if line.margin_discount_percentage > 0:
    #                 # line.margin = (line.landing_cost * line.margin_discount_percentage) / 100
    #                 line.sale_price = line.landing_cost + ((line.landing_cost * line.margin_discount_percentage) / 100)
    #                 line.margin_sale_check = False

    # @api.onchange('sale_price')
    # def ComputeMarginSalePrice(self):
    #
    #     for line in self:
    #         # if line.margin_sale_check == False:
    #         #     line.margin_sale_check = True
    #         #     return
    #         if line.margin:
    #             # if line.margin_discount_percentage == ((line.product_mrp - line.sale_price) / line.margin) * 100:
    #             #     return
    #             line.margin_discount_percentage = ((line.product_mrp - line.sale_price) / line.margin) * 100
    #             # line.margin_sale_check = False
    #         if (not line.product_mrp) and line.landing_cost != 0:
    #             # if line.margin_discount_percentage == ((line.sale_price - line.landing_cost) / line.landing_cost) * 100:
    #             #     return
    #             line.margin_discount_percentage = ((line.sale_price - line.landing_cost) / line.landing_cost) * 100
    #             # line.margin_sale_check = False
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        self.margin = self.product_id.margin
        # self.margin_percentage = self.product_id.margin_percentage
        # self.product_margin = self.product_id.margin
        self.margin_discount_percentage = self.product_id.margin_discount_percentage

    @api.model
    def create(self, vals):

        res = {}

        if vals['invoice_id']:

            invoice_id = self.env['account.invoice'].search([('id', '=', vals['invoice_id'])])
            if not invoice_id:
                return super(AccountInvoiceLine, self).create(vals)

            if invoice_id.type != 'in_invoice':
                return super(AccountInvoiceLine, self).create(vals)

        if vals['product_id']:
            product_id = self.env['product.product'].search([('id', '=', vals['product_id'])])

            if not product_id:
                return super(AccountInvoiceLine, self).create(vals)

            # if 'sale_price' in vals:

            #     product_id.lst_price = vals['sale_price']
      
            if 'margin_discount_percentage' in vals:
            
                product_id.margin_discount_percentage = vals['margin_discount_percentage']

        return super(AccountInvoiceLine, self).create(vals)

    @api.multi
    def write(self, vals):

        res = {}

        if self.invoice_id:

            if self.invoice_id.type != 'in_invoice':
                return super(AccountInvoiceLine, self).write(vals)

        if self.product_id:
            product_id = self.env['product.product'].search([('id', '=', self.product_id.id)])

            if not product_id:
                return super(AccountInvoiceLine, self).write(vals)
            
            if 'margin_discount_percentage' in vals:
                
                product_id.margin_discount_percentage = vals['margin_discount_percentage']
            # if 'sale_price' in vals:
            #     product_id.lst_price = vals['sale_price']
          

        return super(AccountInvoiceLine, self).write(vals)



