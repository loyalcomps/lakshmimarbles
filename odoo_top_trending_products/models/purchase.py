# -*- coding: utf-8 -*-
from openerp import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if ['id', '!=', False] in domain:
            top_most = self.env['ir.config_parameter'].sudo().get_param('top.most.trending.product')
            self.env.cr.execute('select product_id, count(product_id) as cnt from purchase_order_line group by product_id order by cnt desc limit %s' % (top_most))
            po_list = []
            for rec in self.env.cr.fetchall():
                pol_ids = self.env['purchase.order.line'].search([('product_id', '=', rec[0]), ('order_id.state', 'not in', ['sent', 'cancel'])])
                po_list.extend(list(set([x.order_id.id for x in pol_ids])))
            domain.extend([['id', 'in', po_list]])
            domain.extend([['company_id', '=', self.env.user.company_id.id]])
        return super(PurchaseOrder, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
