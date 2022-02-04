# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api
import odoo.addons.decimal_precision as dp

class product_notinpo_compare(models.Model):
    _name = 'report.product.notinpo.compare'

    _auto = False
    rec_name = 'proname'
    # _order = 'date desc'

    product_id = fields.Many2one(
        'product.product', string='Product Variant', readonly=True)

    proname =  fields.Char('Name')

    available_in_pos = fields.Boolean(string='Available In POS',readonly = True)
    barcode = fields.Char(string='Barcode', readonly=True)

    # WARNING : this code doesn't handle uom conversion for the moment
    def _product_notinpo_select(self):
        select = """ SELECT pt.id as id,pp.id as product_id,pt.name as proname,pt.available_in_pos as available_in_pos,
pp.barcode as barcode FROM purchase_order_line pol
RIGHT JOIN product_template pt
            ON pt.id = pol.product_id
LEFT JOIN product_product pp 
            ON pt.id = pp.product_tmpl_id  
WHERE pol.id is null and LENGTH(pp.barcode) = 13
"""
        return select

    def init(self):
        # tools.drop_view_if_exists(self._cr, self._table)
        tools.drop_view_if_exists(self._cr, 'report_product_notinpo_compare')
        self._cr.execute("CREATE OR REPLACE VIEW report_product_notinpo_compare AS (%s)" % (self._product_notinpo_select()))


