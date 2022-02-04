# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api
import odoo.addons.decimal_precision as dp

class product_barcode_compare(models.Model):
    _name = 'report.product.barcode.compare'

    _auto = False
    rec_name = 'proname'
    # _order = 'date desc'

    product_id = fields.Many2one(
        'product.product', string='Product Variant', readonly=True)

    proname =  fields.Char('Name')

    
    quantity = fields.Float(string='Landing Cost', readonly=True,digits=dp.get_precision('Product Price'))
    barcode = fields.Char(string='Barcode', readonly=True)
    # available_in_pos = fields.Boolean(string='Available In POS',readonly = True)

    # WARNING : this code doesn't handle uom conversion for the moment
    def _product_barcode_select(self):
        select = """SELECT pt.id as id, pp.id as product_id,pt.name as proname,pb.quantity as quantity,pb.barcode as barcode FROM product_barcode pb
                    LEFT JOIN product_template pt
            ON pt.id = pb.product_tmpl_id
LEFT JOIN product_product pp 
            ON pt.id = pp.product_tmpl_id 
WHERE quantity > 1
"""
        return select

    def init(self):
        # tools.drop_view_if_exists(self._cr, self._table)
        tools.drop_view_if_exists(self._cr, 'report_product_barcode_compare')
        self._cr.execute("CREATE OR REPLACE VIEW report_product_barcode_compare AS (%s)" % (self._product_barcode_select()))


