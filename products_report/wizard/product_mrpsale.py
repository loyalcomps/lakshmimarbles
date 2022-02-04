import time

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class ProductMRPSale(models.TransientModel):
    _name = "product.mrp.sale.wizard"
    _description = "Product Mrp Sellprice Compare"

    per_amount = fields.Float('Percentage', digits=dp.get_precision('Account'), help="Minimum %",default=85.00)

    @api.multi
    def check_mrp(self):
        mrplines = self.env['report.product.mrpsell.compare']
        mrplines.search([]).unlink()

        lines = []
        per_amount = self.per_amount / 100

        query = '''
        SELECT DISTINCT
            pp.barcode,
            pp.id AS product_id,
            pt.categ_id AS categ_id,
            CAST(COALESCE(pt.product_mrp, '0') AS float) AS product_mrp,
            pt.list_price AS sale_price,
            pt.available_in_pos AS available_in_pos
            FROM product_product pp
            LEFT JOIN product_template pt
            ON pt.id = pp.product_tmpl_id
            LEFT JOIN purchase_order_line pol
            ON pp.id = pol.product_id
        WHERE CAST(COALESCE(pt.product_mrp, '0') AS float) * %s > pt.list_price
        AND pt.active = TRUE and pol.id is not null
        '''

        self.env.cr.execute(query, (per_amount,))

        for row in self.env.cr.dictfetchall():
            res = {
                'product_id': row['product_id'],
                'barcode': row['barcode'],
                'categ_id': row['categ_id'],
                'sale_price': row['sale_price'],
                'available_in_pos': row['available_in_pos'],
                'product_mrp': row['product_mrp']
            }
            mrplines.create(res)

        # if mrplines:
        return mrplines.action_view_mrp_sell()

        # return {'type': 'ir.actions.act_window_close'}
