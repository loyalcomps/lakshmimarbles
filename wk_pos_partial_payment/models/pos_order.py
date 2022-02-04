# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################

from odoo import api, fields, models

class PosOrder(models.Model):
    _inherit = "pos.order"

    invoice_remark = fields.Char(string="Invoice Remark")
    is_partially_paid = fields.Boolean(string="Is Partially Paid")

    @api.model
    def _order_fields(self,ui_order):
        fields_return = super(PosOrder,self)._order_fields(ui_order)
        fields_return.update({'invoice_remark':ui_order.get('invoice_remark', False)})
        fields_return.update({'is_partially_paid':ui_order.get('is_partially_paid', False)})
        return fields_return

    @api.model
    def create_from_ui(self, orders):
        order_ids = return_data = super(PosOrder, self).create_from_ui(orders)

        if type(order_ids) is dict:
            order_ids = return_data.get('order_ids')
        
        order_objs = self.browse(order_ids)
        for order in order_objs:
            if order.invoice_id:
                order.invoice_id.partial_payment_remark = order.invoice_remark
        return return_data
    
    @api.multi
    def action_pos_order_paid(self):
        if self.is_partially_paid:
            self.write({'state': 'paid'})
            return self.create_picking()
        if not self.test_paid():
            raise UserError(_("Order is not paid."))
        self.write({'state': 'paid'})
        return self.create_picking()