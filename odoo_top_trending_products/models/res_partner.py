# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if ['id', '!=', False] in domain:
            top_most = self.env['ir.config_parameter'].sudo().get_param('top.most.trending.product')
            self.env.cr.execute('select product_id, count(product_id) as cnt from sale_order_line group by product_id order by cnt desc limit %s' % (top_most))
            partner_list = []
            for rec in self.env.cr.fetchall():
                sol_ids = self.env['sale.order.line'].search([('product_id', '=', rec[0]), ('order_id.state', 'not in', ['draft', 'sent', 'cancel'])])
                partner_list.extend(list(set([x.order_id.partner_id.id for x in sol_ids])))
            domain.extend([['company_id', '=', self.env.user.company_id.id]])
            id_domain = [x for x in domain if  x[0] == 'id' and x[1] == 'in']
            if id_domain:
                id_domain = id_domain[0]
                domain.remove(id_domain)
                id_domain[2] = list(set(id_domain[2]) & set(list(set(partner_list))))
                domain.extend([id_domain])
            else:
                domain.extend([['id', 'in', list(set(partner_list))]])
        if ['id', '!=', -1] in domain:
            top_most = self.env['ir.config_parameter'].sudo().get_param('top.most.trending.product')
            self.env.cr.execute('select product_id, count(product_id) as cnt from purchase_order_line group by product_id order by cnt desc limit %s' % (top_most))
            product_list = []
            partner_list = []
            for rec in self.env.cr.fetchall():
                pol_ids = self.env['purchase.order.line'].search([('product_id', '=', rec[0]), ('order_id.state', 'not in', ['draft', 'sent', 'cancel'])])
                partner_list.extend(list(set([x.order_id.partner_id.id for x in pol_ids])))
            domain.extend([['company_id', '=', self.env.user.company_id.id]])
            id_domain = [x for x in domain if  x[0] == 'id' and x[1] == 'in']
            if id_domain:
                id_domain = id_domain[0]
                domain.remove(id_domain)
                id_domain[2] = list(set(id_domain[2]) & set(list(set(partner_list))))
                domain.extend([id_domain])
            else:
                domain.extend([['id', 'in', list(set(partner_list))]])
        return super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
