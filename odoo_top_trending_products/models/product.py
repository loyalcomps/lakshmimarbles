# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    template_trending_index_sale = fields.Integer('Trending Index Sale', default=0)
    template_trending_index_purchase = fields.Integer('Trending Index Purchase', default=0)    
    
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if ['id', '!=', False] in domain:
            top_most = self.env['ir.config_parameter'].sudo().get_param('top.most.trending.product')
            self.env.cr.execute('select product_id, count(product_id) as cnt from sale_order_line group by product_id order by cnt desc limit %s' % (top_most))
            product_list = []
            template_dict = {}
            template_list = []
            for rec in self.env.cr.fetchall():
                product_id = self.env['product.product'].search([('id', '=', rec[0])])
                if product_id and product_id.product_tmpl_id:
                    template_dict[product_id.product_tmpl_id.id] = template_dict.get(product_id.product_tmpl_id.id, 0)+ rec[1]
            for rec in template_dict.items():
                template = self.search([('id', '=', rec[0])])
                template and template.write({'template_trending_index_sale': rec[1]})
                template_list.append(rec[0])
            order='template_trending_index_sale desc'
            domain.extend([['company_id', '=', self.env.user.company_id.id]])
            id_domain = [x for x in domain if  x[0] == 'id' and x[1] == 'in']
            if id_domain:
                id_domain = id_domain[0]
                domain.remove(id_domain)
                id_domain[2] = list(set(id_domain[2]) & set(list(set(template_list))))
                domain.extend([id_domain])
            else:
                domain.extend([['id', 'in', list(set(template_list))]])
        if ['id', '!=', -1] in domain:
            top_most = self.env['ir.config_parameter'].sudo().get_param('top.most.trending.product')
            self.env.cr.execute('select product_id, count(product_id) as cnt from purchase_order_line group by product_id order by cnt desc limit %s' % (top_most))
            product_list = []
            template_dict = {}
            template_list = []
            for rec in self.env.cr.fetchall():
                product_id = self.env['product.product'].search([('id', '=', rec[0])])
                if product_id and product_id.product_tmpl_id:
                    template_dict[product_id.product_tmpl_id.id] = template_dict.get(product_id.product_tmpl_id.id, 0)+ rec[1]
            for rec in template_dict.items():
                template = self.search([('id', '=', rec[0])])
                template and template.write({'template_trending_index_purchase': rec[1]})
                template_list.append(rec[0])
            order='template_trending_index_purchase desc'
            domain.extend([['company_id', '=', self.env.user.company_id.id]])
            id_domain = [x for x in domain if  x[0] == 'id' and x[1] == 'in']
            if id_domain:
                id_domain = id_domain[0]
                domain.remove(id_domain)
                id_domain[2] = list(set(id_domain[2]) & set(list(set(template_list))))
                domain.extend([id_domain])
            else:
                domain.extend([['id', 'in', list(set(template_list))]])
        return super(ProductTemplate, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        
class ProductProduct(models.Model):
    _inherit = "product.product"
    
    product_trending_index_sale = fields.Integer('Trending Index Sale', default=0)
    product_trending_index_purchase = fields.Integer('Trending Index Purchase', default=0)    
    
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if ['id', '!=', False] in domain:
            top_most = self.env['ir.config_parameter'].sudo().get_param('top.most.trending.product')
            self.env.cr.execute('select product_id, count(product_id) as cnt from sale_order_line group by product_id order by cnt desc limit %s' % (top_most))
            product_list = []
            for rec in self.env.cr.fetchall():
                product = self.search([('id', '=', rec[0])])
                product and product.write({'product_trending_index_sale': rec[1]})
                product_list.append(rec[0])
            order='product_trending_index_sale desc'
            domain.extend([['company_id', '=', self.env.user.company_id.id]])
            id_domain = [x for x in domain if  x[0] == 'id' and x[1] == 'in']
            if id_domain:
                id_domain = id_domain[0]
                domain.remove(id_domain)
                id_domain[2] = list(set(id_domain[2]) & set(list(set(product_list))))
                domain.extend([id_domain])
            else:
                domain.extend([['id', 'in', list(set(product_list))]])
        if ['id', '!=', -1] in domain:
            top_most = self.env['ir.config_parameter'].sudo().get_param('top.most.trending.product')
            self.env.cr.execute('select product_id, count(product_id) as cnt from purchase_order_line group by product_id order by cnt desc limit %s' % (top_most))
            product_list = []
            for rec in self.env.cr.fetchall():
                product = self.search([('id', '=', rec[0])])
                product and product.write({'product_trending_index_purchase': rec[1]})
                product_list.append(rec[0])
            order='product_trending_index_purchase desc'
            domain.extend([['company_id', '=', self.env.user.company_id.id]])
            id_domain = [x for x in domain if  x[0] == 'id' and x[1] == 'in']
            if id_domain:
                id_domain = id_domain[0]
                domain.remove(id_domain)
                id_domain[2] = list(set(id_domain[2]) & set(list(set(product_list))))
                domain.extend([id_domain])
            else:
                domain.extend([['id', 'in', list(set(product_list))]])
        return super(ProductProduct, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
