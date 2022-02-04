# -*- coding: utf-8 -*-
from openerp import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if ['id', '!=', False] in domain:
            top_most = self.env['ir.config_parameter'].sudo().get_param('top.most.trending.product')
            self.env.cr.execute('select product_id, count(product_id) as cnt from sale_order_line group by product_id order by cnt desc limit %s' % (top_most))
            so_list = []
            for rec in self.env.cr.fetchall():
                sol_ids = self.env['sale.order.line'].search([('product_id', '=', rec[0]), ('order_id.state', 'not in', ['draft', 'sent', 'cancel'])])
                so_list.extend(list(set([x.order_id.id for x in sol_ids])))
            domain.extend([['id', 'in', so_list]])
            domain.extend([['company_id', '=', self.env.user.company_id.id]])
        return super(SaleOrder, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
