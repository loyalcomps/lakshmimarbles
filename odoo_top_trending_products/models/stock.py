# -*- coding: utf-8 -*-
from openerp import fields, models, api


class StockQuant(models.Model):
    _inherit = "stock.quant"
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if ['id', '!=', False] in domain:
            top_most = self.env['ir.config_parameter'].sudo().get_param('top.most.trending.product')
            self.env.cr.execute('select product_id, count(product_id) as cnt from sale_order_line group by product_id order by cnt desc limit %s' % (top_most))
            product_list = []
            for rec in self.env.cr.fetchall():
                product = self.env['product.product'].sudo().search([('id', '=', rec[0])])
                product_list.append(rec[0])
            domain.extend([['company_id', '=', self.env.user.company_id.id]])
            id_domain = [x for x in domain if  x[0] == 'product_id' and x[1] == 'in']
            if id_domain:
                id_domain = id_domain[0]
                domain.remove(id_domain)
                id_domain[2] = list(set(id_domain[2]) & set(list(set(product_list))))
                domain.extend([id_domain])
            else:
                domain.extend([['product_id', 'in', list(set(product_list))]])
        if ['id', '!=', -1] in domain:
            top_most = self.env['ir.config_parameter'].sudo().get_param('top.most.trending.product')
            self.env.cr.execute('select product_id, count(product_id) as cnt from purchase_order_line group by product_id order by cnt desc limit %s' % (top_most))
            product_list = []
            for rec in self.env.cr.fetchall():
                product = self.search([('product_id', '=', rec[0])])
                product_list.append(rec[0])
            domain.extend([['company_id', '=', self.env.user.company_id.id]])
            id_domain = [x for x in domain if  x[0] == 'product_id' and x[1] == 'in']
            if id_domain:
                id_domain = id_domain[0]
                domain.remove(id_domain)
                id_domain[2] = list(set(id_domain[2]) & set(list(set(product_list))))
                domain.extend([id_domain])
            else:
                domain.extend([['product_id', 'in', list(set(product_list))]])
        return super(StockQuant, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
