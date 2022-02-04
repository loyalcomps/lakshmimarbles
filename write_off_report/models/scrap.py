# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockScrap(models.Model):
    _inherit = "stock.scrap"

    onhand_qty = fields.Float(string='Onhand',)
    cost = fields.Float(string="Cost",related='product_id.standard_price')

    @api.onchange('product_id','location_id')
    def get_onhand_qty(self):
        query = '''select sum(qty) as qty from stock_quant where product_id=%s and location_id=%s
                    '''
        self.env.cr.execute(query, (self.product_id.id, self.location_id.id))
        for row in self.env.cr.dictfetchall():
            self.onhand_qty=row['qty'] if row['qty'] else 0


class StockMove(models.Model):
    _inherit = "stock.move"

    onhand_qty = fields.Float(string='Onhand',)



    def set_default_qty_from_product(self):
        """ Set price to move, important in inter-company moves or receipts with only one partner """
        for move in self:
            query='''select sum(qty) as qty from stock_quant where product_id=%s and location_id=%s
            '''
            self.env.cr.execute(query, (move.product_id.id, move.location_id.id))
            for row in self.env.cr.dictfetchall():
                move.write({'onhand_qty': row['qty'] if row['qty'] else 0})


    @api.multi
    def action_confirm(self):
        self.set_default_qty_from_product()
        res= super(StockMove, self).action_confirm()
        return res


