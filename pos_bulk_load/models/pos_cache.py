# -*- coding: utf-8 -*-
from odoo import api, models, fields, registry
import logging
import json
import ast

_logger = logging.getLogger(__name__)


class pos_cache_database(models.Model):
    _name = "pos.cache.database"

    res_id = fields.Char('Res id')
    res_model = fields.Char('Res model')
    data = fields.Text('Value')

    def get_fields_by_model(self, model_name):
        params = self.env['ir.config_parameter'].sudo().get_param(model_name)
        if not params:
            list_fields = self.env[model_name].fields_get()
            fields_load = []
            for k, v in list_fields.items():
                if v['type'] not in ['one2many', 'binary']:
                    fields_load.append(k)
            return fields_load
        else:
            params = ast.literal_eval(params)
            return params.get('fields', [])

    @api.model
    def cache_all_datas(self, model, datas):
        for data in datas:
            records = self.search([('res_id', '=', data['id']), ('res_model', '=', model)])
            if not records:
                self.env.cr.execute("insert into pos_cache_database (res_id, res_model, data) VALUES (%s, %s, %s)",
                                    (data['id'], model, json.dumps(data),))
            _logger.info('{cached} model %s' % model)
            records.write({
                'data': json.dumps(data)
            })
        return True

    @api.model
    def add_cache_record(self, record):
        fields_load = self.get_fields_by_model(record._name)
        if not fields_load:
            _logger.error('{error} could not find field need to read table: %s' % record._name)
            return False
        datas = self.env[record._name].search_read([('id', '=', record.id)], fields_load)
        if datas:
            _logger.info('{cached} record ID %s of table %s' % (record.id, record._name))
            data = datas[0]
            records = self.search([('res_id', '=', data['id']), ('res_model', '=', record._name)])
            if not records:
                self.create({
                    'res_id': data['id'],
                    'res_model': record._name,
                    'data': json.dumps(data)
                })
            else:
                records.write({
                    'data': json.dumps(data)
                })
        return True

    @api.model
    def remove_cache_record(self, record):
        fields_load = self.get_fields_by_model(record._name)
        if not fields_load:
            _logger.error('{error} could not find field need to read table: %s' % record._name)
            return False
        datas = self.env[record._name].search_read([('id', '=', record.id)], fields_load)
        if datas:
            data = datas[0]
            return self.search([('res_id', '=', data['id']), ('res_model', '=', record._name)]).unlink()
        else:
            return False

    @api.model
    def store_pos_models(self, model_datas):
        set_param = self.env['ir.config_parameter'].sudo().set_param
        for model_name, value in model_datas.items():
            set_param(model_name, value)
        return True

    @api.model
    def get_product_available_all_stock_location(self, stock_location_id):
        sql = """
        with
          uitstock as (
            select
              t.name product, sum(product_qty) sumout, m.product_id, m.product_uom 
            from stock_move m 
              left join product_product p on m.product_id = p.id 
              left join product_template t on p.product_tmpl_id = t.id
            where
              m.state like 'done' 
              and m.location_id in (select id from stock_location where usage like 'internal') 
              and m.location_dest_id not in (select id from stock_location where usage like 'internal') 
            group by product_id,product_uom, t.name order by t.name asc
          ),
          instock as (
            select
              t.list_price purchaseprice, t.name product, sum(product_qty) sumin, m.product_id, m.product_uom
            from stock_move m
              left join product_product p on m.product_id = p.id
              left join product_template t on p.product_tmpl_id = t.id
            where 
              m.state like 'done' and m.location_id not in (select id from stock_location where usage like 'internal')
              and m.location_dest_id in (select id from stock_location where usage like 'internal')
            group by product_id,product_uom, t.name, t.list_price order by t.name asc
          ) 
        select
          i.product, sumin-coalesce(sumout,0) AS stock, sumin, sumout, purchaseprice, ((sumin-coalesce(sumout,0)) * purchaseprice) as stockvalue
        from uitstock u 
          full outer join instock i on u.product = i.product
        """

    @api.model
    def get_product_available_filter_by_stock_location_id(self, stock_location_id):
        sql = """
        with
          uitstock as (
            select
              t.name product, sum(product_qty) sumout, m.product_id, m.product_uom 
            from stock_move m 
              left join product_product p on m.product_id = p.id 
              left join product_template t on p.product_tmpl_id = t.id
            where
              m.state like 'done'
              and t.type = 'product' 
              and m.location_id in (select id from stock_location where id=%s) 
              and m.location_dest_id not in (select id from stock_location where id=%s) 
            group by product_id,product_uom, t.name order by t.name asc
          ),
          instock as (
            select
              t.list_price purchaseprice, t.name product, sum(product_qty) sumin, m.product_id, m.product_uom
            from stock_move m
              left join product_product p on m.product_id = p.id
              left join product_template t on p.product_tmpl_id = t.id
            where 
              m.state like 'done' and m.location_id not in (select id from stock_location where id=%s)
              and m.location_dest_id in (select id from stock_location where id=%s)
            group by product_id,product_uom, t.name, t.list_price order by t.name asc
          ) 
        select
          i.product_id, i.product, sumin-coalesce(sumout,0) AS stock, sumin, sumout, purchaseprice, ((sumin-coalesce(sumout,0)) * purchaseprice) as stockvalue
        from uitstock u 
          full outer join instock i on u.product = i.product
        """ % (stock_location_id, stock_location_id, stock_location_id, stock_location_id)
        self.env.cr.execute(sql)
        results = self.env.cr.fetchall()
        pos_data = {}
        for result in results:
            if result[0]:
                pos_data[result[0]] = result[2]
        return pos_data
