# -*- coding: utf-8 -*-

from odoo import models, fields, api,SUPERUSER_ID
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class purchase_article_no(models.Model):
    _inherit = 'purchase.order.line'

    product_article_no  = fields.Integer('Article No.',)

    @api.onchange('product_article_no')
    def load_product(self):
        result = {}
        if not self.product_article_no:
            result['domain'] = {'product_id': [('id', 'in', self.env['product.product'].search([]).ids)]}
            return result
        if self.product_article_no:

            result['domain'] = {'product_id': [('id', '=', self.product_article_no)]}
            return result

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(purchase_article_no, self).onchange_product_id()

        self.product_article_no = self.product_id.id

    # @api.onchange('product_article_no', 'product_id')
    # def _onchange_product_article_no(self):
    #     product_rec = self.env['product.product']
    #     product_ids = []
    #     result = {}
    #     if self.product_article_no:
    #         product = product_rec.search([('id', '=', self.product_article_no)])
    #         if product:
    #             product_ids.append(product.id)
    #
    #
    #         result['domain'] = {'product_id': [('id', 'in', product_ids)]}
    #
    #         return result
    #     else:
    #         products = self.env['product.product'].search([]).ids
    #         result['domain'] = {'product_id': [('id', 'in', products)]}
    #
    #         return result

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    invarticle_no = fields.Integer('Article No.',)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()

        self.invarticle_no = self.product_id.id

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        var = {}

        for l in line:

            var = {

                    'invarticle_no':l.product_article_no,
            }

        res.update(var)
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    article = fields.Integer('Article No.',)



    @api.onchange('article')
    def load_product_based_article(self):

        if not self.article:
            return {}
        product_details = {}
        product_id = self.env['product.product'].browse(self.article)
        if not product_id:
            self.article = False
            return {

                'warning': {'title': 'Error!', 'message': 'Please enter the correct barcode'},
                'value': {
                    'barcode': False,
                    #                      'flat': None,
                }
            }
        product_lang = product_id.with_context({
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
                product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        else:
            taxes_id = fpos.map_tax(product_id.supplier_taxes_id)

        order_line_var = self.env['purchase.order.line']
        values={
            'product_id':product_id.id,
            'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'product_uom': product_id.uom_po_id.id or product_id.uom_id.id,
            'name':name,
            'taxes_id':taxes_id,
            'barcode':product_id.barcode,
            'hsn':product_id.hsn,
            'product_article_no':product_id.id,
            'product_mrp':product_id.product_mrp,
            'sale_price':product_id.lst_price,
            'product_bool':False,

        }

        order_line_var1 = order_line_var.new(values)
        order_line_var1._suggest_quantity()
        order_line_var1._onchange_quantity()
        # order_line_var += order_line_var1
        self.order_line += order_line_var1
        self.article = False
