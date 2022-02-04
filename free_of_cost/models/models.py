# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    free_qty = fields.Float(string='Free Quantity',default=0)

    # passing free quantity to stock moves
    @api.multi
    def _create_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._create_stock_moves(picking)
        for moves in res:
            for line in self:
                if moves.purchase_line_id.id == line.id:
                    moves.update({'product_uom_qty': line.product_qty + line.free_qty})

        return res

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    free_qty = fields.Float(string='Free Quantity', default=0)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        res.update({
            'free_qty': line.free_qty,
            'quantity': line.product_qty,
        })
        return res

