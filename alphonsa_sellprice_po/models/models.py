# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class Alphonsa_sellprice(models.Model):
    _inherit = 'purchase.order.line'

    sale_price = fields.Float(string="Sale Price", default=0.0)
    is_color = fields.Boolean('Validation Color', compute='_compute_color')

    @api.model
    def create(self, vals):

        if vals['product_id']:

            product_id = self.env['product.product'].search([('id', '=', vals['product_id'])])

            if not product_id:
                return super(Alphonsa_sellprice, self).create(vals)

            # if 'sale_price' in vals:
            #     product_id.lst_price = vals['sale_price']

        return super(Alphonsa_sellprice, self).create(vals)

    @api.multi
    def write(self, vals):

        if self.product_id:
            product_id = self.env['product.product'].search([('id', '=', self.product_id.id)])

            if not product_id:
                return super(Alphonsa_sellprice, self).write(vals)

            # if 'sale_price' in vals:
            #     product_id.lst_price = vals['sale_price']

        return super(Alphonsa_sellprice, self).write(vals)

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(Alphonsa_sellprice, self).onchange_product_id()

        self.sale_price = self.product_id.lst_price

    @api.multi
    @api.constrains('product_mrp', 'sale_price')
    def _check_mrp_landing_cost_sale_price(self):

        for line in self:
            if line.product_mrp < line.sale_price:
                raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ")% line.product_id.name)


    @api.one
    @api.depends('product_mrp', 'sale_price')
    def _compute_color(self):

        for line in self:
            line.is_color = False


            if line.product_mrp < line.sale_price:
                line.is_color = True


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # def _prepare_invoice_line_from_po_line(self, line):
    #     res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
    #
    #     for l in line:
    #         var = {
    #
    #             'sale_price': l.product_id.lst_price,
    #
    #         }
    #         _logger.info('Sale Price %s', l.sale_price)
    #     res.update(var)
    #     return res




class AlphonsaAccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    sale_price = fields.Float(string="Sale Price", default=0.0)
    is_color = fields.Boolean('Validation Color',compute='_compute_color')

    @api.model
    def create(self, vals):

        res = {}

        if vals['invoice_id']:

            invoice_id = self.env['account.invoice'].search([('id', '=', vals['invoice_id'])])
            if not invoice_id:
                return super(AlphonsaAccountInvoiceLine, self).create(vals)

            if invoice_id.type != 'in_invoice':
                return super(AlphonsaAccountInvoiceLine, self).create(vals)

        if vals['product_id']:

            product_id = self.env['product.product'].search([('id', '=', vals['product_id'])])

            if not product_id:
                return super(AlphonsaAccountInvoiceLine, self).create(vals)

            # if 'sale_price' in vals:
            #     product_id.lst_price = vals['sale_price']

        return super(AlphonsaAccountInvoiceLine, self).create(vals)

    @api.multi
    def write(self, vals):

        res = {}

        if self.invoice_id:

            if self.invoice_id.type != 'in_invoice':
                return super(AlphonsaAccountInvoiceLine, self).write(vals)

        if self.product_id:
            product_id = self.env['product.product'].search([('id', '=', self.product_id.id)])

            if not product_id:
                return super(AlphonsaAccountInvoiceLine, self).write(vals)

            # if 'sale_price' in vals:
            #     product_id.lst_price = vals['sale_price']

        return super(AlphonsaAccountInvoiceLine, self).write(vals)

    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     res = super(AlphonsaAccountInvoiceLine, self)._onchange_product_id()

    #     self.sale_price = self.product_id.lst_price

    @api.multi
    @api.constrains('product_mrp', 'sale_price','asset_category_id')
    def _check_mrp_landing_cost_sale_price(self):

        for line in self:

            if line.invoice_id.type != 'in_invoice':
                return
            if line.asset_category_id:

                return

            # if line.product_mrp < line.landing_cost:
            #     raise ValidationError(_("Cannot Give MRP Less Than Landing Cost (%s)")% line.product_id.name)
            if line.product_mrp < line.sale_price:
                # line.is_color = True
                # raise ValidationError("Cannot give sale price greater than mrp.")
                raise ValidationError(_("Cannot Give Sale Price Greater Than MRP For (%s) ") % line.product_id.name)
            # if line.sale_price < line.landing_cost:
            #     raise ValidationError(_("Cannot Give Sale Price Less Than Landing Cost (%s)") % line.product_id.name)

    @api.one
    @api.depends('product_mrp','sale_price','landing_cost','asset_category_id')
    def _compute_color(self):

        for line in self:
            line.is_color = False

            if line.invoice_id.type != 'in_invoice':
                return
            if line.asset_category_id:
                line.is_color = False
                return

            if line.product_mrp < line.landing_cost:
                line.is_color = True

            if line.product_mrp < line.sale_price:
                line.is_color = True

            if line.sale_price < line.landing_cost:
                line.is_color = True

