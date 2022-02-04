# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import exceptions, _
from odoo.exceptions import UserError, ValidationError
import operator
from odoo.exceptions import Warning


    # query='''SELECT *
    #         FROM information_schema.constraint_table_usage
    #         WHERE table_name = 'purchase.order.line';
    #
    #         ALTER TABLE purchase_order_line DROP CONSTRAINT barcode;'''
    #
    # def grand_barcode_unque(self):
    #
    #
    #
    #     query='''select barcode
    #         from purchase_order_line
    #         GROUP BY barcode,product_id
    #         HAVING COUNT(barcode) > 1 and product_id = %s'''
    #
    #     self.env.cr.execute(query,(self.product_id))
    #
    #
    #
    #
    #
    #
    #
    # @api.one
    # @api.constrains('barcode',)
    # def check_unique_barcode(self):
    #     if self.barcode :
    #         filters = [('barcode', '=', self.barcode)]
    #         prod_ids = self.search(filters)
    #         if len(prod_ids) > 1:
    #             raise ValidationError("A barcode can only be assigned to one product ! %s " % self.barcode)


# class grand_barcode_color(models.Model):
#     _inherit = 'product.product'
#
#     @api.model
#     @api.multi
#     @api.constrains('barcode')
#     def _check_barcode(self):
#         for record in self:
#             if len(record.barcode )> 1:
#                 raise ValidationError("A barcode can only be assigned to one product ! the product is :%s"%record.name)

#     _constraints = [
#         (_check_barcode, u'A barcode can only be assigned to one product ! ', ['barcode']),
#     ]
    # @api.model
    # @api.constrains('barcode')
    # def _check_unique_constraint(self):
    #     for line in self:
    #         if line.barcode:
    #             if len(self.search([('barcode', '=', line.barcode)])) > 1:
    #                 raise ValidationError("product %s(product_id)")
    #         else:
    #             pass

    # @api.model
    # def _auto_init(self):
    #     res = super(grand_barcode_color, self)._auto_init()
    #     self._sql_constraints = [
    #         ('barcode_uniq', 'unique(barcode)', _("Barcode should be unique by product!")), ]
    #     return res
class uni_barcode(models.Model):
    _inherit = "purchase.order.line"


    @api.multi
    @api.depends('barcode')
    def _color_purchase(self):

        for line in self:

            s = []
            po_barcode = self.env['product.product'].search([('barcode', '=', line.barcode)])
            for x in po_barcode:
                if x.id!=line.product_id.id:
                    line.barcode_color = True

    barcode_color = fields.Boolean(string="COLOR",compute=_color_purchase,default=False)

    # @api.multi
    # @api.depends('barcode')
    # def Purchase_barcode_color(self):
    #     for line in self:
    #         if line.product_id.barcode == line.barcode:
    #             line.barcode_color == True
    #
    #         else:
    #             line.barcode_color == False
    #     return

class AccountInvoice(models.Model):
    _inherit = "account.invoice.line"


    @api.multi
    @api.depends('barcode')
    def _color_purchase(self):

        for line in self:

            s = []
            po_barcode = self.env['product.product'].search([('barcode', '=', line.barcode)])
            for x in po_barcode:
                if x.id!=line.product_id.id:
                    line.barcode_color = True

    barcode_color = fields.Boolean(string="COLOR", compute=_color_purchase, default=False)



