# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_move(models.Model):
    _inherit = "stock.move"

    @api.model
    def create(self, vals):
        """
        if move create from pos order line
        and pol have uom ID and pol uom ID difference with current move
        we'll re-update product_uom of move
        FOR linked stock on hand of product
        :return:
        """
        move = super(stock_move, self).create(vals)
        order_lines = self.env['pos.order.line'].search([
            ('name', '=', move.name),
            ('product_id', '=', move.product_id.id),
            ('qty', '=', move.product_uom_qty)
        ])
        for line in order_lines:
            if line.uom_id and line.uom_id != move.product_uom:
                move.write({
                    'product_uom': line.uom_id.id
                })
        return move