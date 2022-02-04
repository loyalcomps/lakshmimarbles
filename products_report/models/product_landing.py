# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api
import odoo.addons.decimal_precision as dp

class product_landing_compare(models.Model):
    _name = 'report.product.landing.compare'

    _auto = False
    rec_name = 'proname'
    # _order = 'date desc'

    product_id = fields.Many2one(
        'product.product', string='Product Variant', readonly=True)

    proname =  fields.Char('Name')

    categ_id = fields.Many2one(
        'product.category', string='Product Category', readonly=True)
    stock = fields.Float(string='On Hand', readonly=True)
    landing_cost = fields.Float(string='Landing Cost', readonly=True,digits=dp.get_precision('Product Price'))
    sale_price = fields.Float(string='Sale Price', readonly=True,digits=dp.get_precision('Product Price'))
    available_in_pos = fields.Boolean(string='Available In POS',readonly = True)

    # WARNING : this code doesn't handle uom conversion for the moment
    def _product_landing_select(self):
        select = """SELECT
            min(pp.id) as id,
            pp.id AS product_id,
            pt.name AS proname,
            max(pt.categ_id) as categ_id,
            COALESCE(SUM(sh.quantity), '0') AS stock,
            MAX(CAST(COALESCE(pt.landing_cost, '0') AS float)) AS landing_cost,
            MAX(pt.list_price) AS sale_price,
            pt.available_in_pos as available_in_pos
            FROM product_product pp
            LEFT JOIN product_template pt
            ON pt.id = pp.product_tmpl_id
            LEFT JOIN stock_history sh
            ON pp.id = sh.product_id
            WHERE CAST(COALESCE(pt.landing_cost, '0') AS float) > pt.list_price and pt.active = True
            GROUP BY pp.id,
            pt.available_in_pos,
            pt.name
            ORDER BY pt.name """
        return select

    def init(self):
        # tools.drop_view_if_exists(self._cr, self._table)
        tools.drop_view_if_exists(self._cr, 'report_product_landing_compare')
        self._cr.execute("CREATE OR REPLACE VIEW report_product_landing_compare AS (%s)" % (self._product_landing_select()))


