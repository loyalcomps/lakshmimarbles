# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(
        selection_add=[('waiting_for_approval', 'Waiting For Approval'), ('approved', 'Approved'),
                       ('rejected', 'Rejected')])

    @api.multi
    def action_confirm(self):
        for order in self:
            if order.state!= 'approved':
                product_list = [line.product_id.name for line in order.order_line if line.price_unit<line.product_id.min_sale_amt]
                if product_list:
                    if len(product_list) > 1:
                        message = _(
                            "The following products Price is less than the affordable price:") + '\n\n'
                        message += '\n'.join(map(str, product_list))
                        message += '\n\nClick on "Ask for Approval" for Higher value.'
                    else:
                        message = _(
                            "The following product Price is less than the affordable price:") + '\n\n'
                        message += '\n'.join(map(str, product_list))
                        message += '\n\nClick on "Ask for Approval" for Higher value.'
                    raise UserError(_(message))

                # for line in order.order_line:
                #     if line.price_unit<line.product_id.min_sale_amt:
                #
                #         raise UserError(_(
                #             'Price unit is less than affordable price for %s.Click on "Ask for Approval" for Higher value.')
                #         % (line.product_id.name))
            super(SaleOrder, self).action_confirm()
    # @api.multi
    # def confirm_quotation(self):
    #     for order in self:
    #         for line in order.order_line:
    #             if line.price_unit<line.product_id.min_sale_amt:
    #
    #                 raise UserError(_(
    #                     'Price unit is less than affordable price for %s.Click on "Ask for Approval" for Higher value.')
    #                 % (line.product_id.name))
    #
    #         order.state = 'approved'

    @api.multi
    def action_sales_approvals(self):
        for order in self:
            order.state = 'waiting_for_approval'

    @api.multi
    def md_approval(self):
        for order in self:
            order.state = 'approved'

    @api.multi
    def md_refused(self):
        for order in self:
            order.state = 'rejected'

    @api.multi
    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent', 'rejected'])
        orders.write({
            'state': 'draft',
            'procurement_group_id': False,
        })
        return orders.mapped('order_line').mapped('procurement_ids').write({'sale_line_id': False})
