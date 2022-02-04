# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api,_
import odoo.addons.decimal_precision as dp

class product_mrpsell_compare(models.TransientModel):
    _name = 'report.product.mrpsell.compare'
    _rec_name= 'barcode'
    # _auto = False
    # _order = 'date desc'

    product_id = fields.Many2one(
        'product.product', string='Product Variant', readonly=True)
    barcode = fields.Char(string='Barcode',readonly=True)
    categ_id = fields.Many2one(
        'product.category', string='Product Category', readonly=True)
    product_mrp = fields.Float(string='MRP', readonly=True, digits=dp.get_precision('Product Price'))
    sale_price = fields.Float(string='Sale Price', readonly=True, digits=dp.get_precision('Product Price'))
    available_in_pos = fields.Boolean(string='Available In POS', readonly=True)

    @api.multi
    def action_view_mrp_sell(self):

        mrps = self.search([])
        action = self.env.ref('products_report.report_product_mrpsell_compare_action').read()[0]
        if len(mrps) > 1:
            action['domain'] = [('id', 'in', mrps.ids)]
        elif len(mrps) == 1:
            action['views'] = [(self.env.ref('product_reports.report_product_mrpsell_compare_form').id, 'form')]
            action['res_id'] = mrps.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action






