odoo.define('pos_bulk_load.bulk', function (require) {
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');

    var _super_PosModel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var self = this;
            this.min_load = 0;
            this.max_load = 2000;
            this.next_load = 2000;
            this.cache_datas = {
                'product.product': [],
                'res.partner': [],
//                'account.invoice': [],
//                'pos.order': [],
//                'pos.order.line': []
            };
            setInterval(function () {
                self.store_pos_models();
            }, 5000);
            return _super_PosModel.initialize.apply(this, arguments);
        },
        // auto store params to system parameter
        store_pos_models: function () {
            var models = {};
            var tmp = {};
            for (var i = 0; i < this.models.length; i++) {
                var model = this.models[i];
                if (model.model == 'res.partner' || model.model == 'product.product' ) {
                    var fields = typeof model.fields === 'function' ? model.fields(self, tmp) : model.fields;
                    var context = {};
                    if (this.version.server_serie == "10.0") {
                        if (model.model == 'product.product') {
                            context = {
                                pricelist: this.config.pricelist_id[0],
                                display_default_code: false
                            }
                        }
                    }
                    else if (this.version.server_serie == "11.0") {
                        if (model.model == 'product.product') {
                            context = {
                                pricelist: this.config.pricelist_id[0],
                                display_default_code: false
                            }
                        }
                    }
                    var domain = typeof model.domain === 'function' ? model.domain(self, tmp) : model.domain;
                    models[model.model] = {
                        fields: fields,
                        context: context,
                        domain: domain
                    }
                }
            }
            rpc.query({
                model: 'pos.cache.database',
                method: 'store_pos_models',
                args:
                    [models]
            });
        },
        cache_all_datas: function (model, datas) {
            var cache_datas = rpc.query({
                model: 'pos.cache.database',
                method: 'cache_all_datas',
                args:
                    [model, datas],
                context: {
                    pos: true
                }
            });
            cache_datas.then(function () {
            }).fail(function (type, error) {
                if (error.code === 200) {
                    event.preventDefault();
                    console.error(error.data.message);
                }
            });
        },
        load_cache: function (model) {
            var loaded = new $.Deferred();
            if (!model) {
                return loaded.resolve();
            }
            var self = this;
            var tmp = {}
            var fields = model.fields;
            var context = model.context || {};

            function load_data(min_id, max_id) {
                var domain = [['id', '>=', min_id], ['id', '<=', max_id]];
                if (model['model'] == 'product.product') {
                    domain.push(['available_in_pos', '=', true]);
                    context = {
                        location: self.config.stock_location_id[0],
                        pricelist: self.pricelist.id,
                        display_default_code: false
                    }
                }
                if (model['model'] == 'res.partner') {
                    domain.push(['customer', '=', true]);
                }
//                if (model == 'pos.order' || model == 'account.invoice') {
//                    domain.push(['state', '!=', 'cancel'])
//                }
                var params = {
                    model: model.model,
                    method: 'search_read',
                    domain: domain,
                    fields: fields,
                    context: context
                };
                self.chrome.loading_message(_t('The first installing model ') + ' ' + (model.model || '') + ', cached: ' + max_id);
                rpc.query(params).then(function (result) {
                    self.cache_datas[model['model']] = self.cache_datas[model['model']].concat(result); // before loaded, we're store datas, because odoo change datas
                    $.when(self.cache_all_datas(model['model'], result)).then(
                        $.when(model.loaded(self, result, tmp))
                            .then(function () {
                                    if (result.length > 0) {
                                        min_id += self.next_load;
                                        max_id += self.next_load;
                                        load_data(min_id, max_id);
                                    } else {
                                        loaded.resolve();
                                    }
                                },
                                function (err) {
                                    loaded.reject(err);
                                })
                    )
                });
            }

            load_data(this.min_load, this.max_load);
            return loaded;
        },
        load_server_data: function () {
            var self = this;
            var models_load_background = [];
            this.mode_cache_by_name = {}
            // remove product loaded
            var product_index = _.findIndex(self.models, function (model) {
                return model.model == 'product.product';
            });
            if (product_index !== -1) {
                var product_model = this.models[product_index];
                this.mode_cache_by_name[product_model['model']] = product_model;
                models_load_background.push(this.models[product_index]);
                self.models.splice(product_index, 1);
            }
            // remove partner loaded
            var partner_index = _.findIndex(self.models, function (model) {
                return model.model == 'res.partner';
            });
            if (partner_index !== -1) {
                var partner_model = this.models[partner_index];
                this.mode_cache_by_name[partner_model['model']] = partner_model;
                models_load_background.push(partner_model);
                self.models.splice(partner_index, 1);
            }
            // remove invoice loaded
//            var invoice_index = _.findIndex(self.models, function (model) {
//                return model.model == 'account.invoice';
//            });
//            if (invoice_index !== -1) {
//                var invoice_model = this.models[invoice_index];
//                this.mode_cache_by_name[invoice_model['model']] = invoice_model;
//                models_load_background.push(invoice_model);
//                self.models.splice(invoice_index, 1);
//            }
            // remove pos order
//            var pos_order_index = _.findIndex(self.models, function (model) {
//                return model.model == 'pos.order';
//            });
//            if (pos_order_index !== -1) {
//                var pos_order_model = this.models[pos_order_index];
//                this.mode_cache_by_name[pos_order_model['model']] = pos_order_model;
//                models_load_background.push(pos_order_model);
//                self.models.splice(pos_order_index, 1);
//            }
//            // remove pos order line
//            var pos_order_line_index = _.findIndex(self.models, function (model) {
//                return model.model == 'pos.order.line';
//            });
//            if (pos_order_line_index !== -1) {
//                var pos_order_line_model = this.models[pos_order_line_index];
//                this.mode_cache_by_name[pos_order_line_model['model']] = pos_order_line_model;
//                models_load_background.push(pos_order_line_model);
//                self.models.splice(pos_order_line_index, 1);
//            }
            this.models_load_background = models_load_background;
            this.products = [];
            return _super_PosModel.load_server_data.apply(this, arguments).then(function () {
                for (var model_index in self.models_load_background) {
                    self.models.push(self.models_load_background[model_index]);
                }
                self.chrome.loading_message(_t('Waiting few seconds for get datas'), 1);
                var params = {
                    model: 'pos.cache.database',
                    method: 'search_read',
                    domain: [],
                    fields: ['res_id', 'res_model', 'data'],
                    context: {}
                };
                var cache_records = rpc.query(params);
                return cache_records.then(function (datas) {
                    var product_model = self.mode_cache_by_name['product.product'];
                    var partner_model = self.mode_cache_by_name['res.partner'];
//                    var invoice_model = self.mode_cache_by_name['account.invoice'];
//                    var po_model = self.mode_cache_by_name['pos.order'];
//                    var pol_model = self.mode_cache_by_name['pos.order.line'];
                    var partners_value = _.filter(datas, function (data) {
                        return data['res_model'] == 'res.partner';
                    });
                    var partners = [];
                    for (var i = 0; i < partners_value.length; i++) {
                        partners.push(JSON.parse(partners_value[i]['data']))
                    }
                    self.products = [];
                    var product_ids = [];
                    var products_value = _.filter(datas, function (data) {
                        return data['res_model'] == 'product.product';
                    });
                    for (var i = 0; i < products_value.length; i++) {
                        var product = JSON.parse(products_value[i]['data']);
                        product['price'] = product['list_price']
                        self.products.push(product);
                        product_ids.push(product['id'])
                    }
                    if (partners.length > 0 && product_ids.length > 0) {
                        partner_model.loaded(self, partners, {});
                        // start load invoices
//                        var invoices_value = _.filter(datas, function (data) {
//                            return data['res_model'] == 'account.invoice';
//                        });
//                        var invoices = [];
//                        for (var i = 0; i < invoices_value.length; i++) {
//                            invoices.push(JSON.parse(invoices_value[i]['data']))
//                        }
//                        invoice_model.loaded(self, invoices, {})
//                        // start load orders
//                        var orders_value = _.filter(datas, function (data) {
//                            return data['res_model'] == 'pos.order';
//                        });
//                        var orders = [];
//                        for (var i = 0; i < orders_value.length; i++) {
//                            orders.push(JSON.parse(orders_value[i]['data']))
//                        }
//                        pos_order_model.loaded(self, orders, {});
//                        // start load order lines
//                        var order_lines_value = _.filter(datas, function (data) {
//                            return data['res_model'] == 'pos.order.line';
//                        });
//                        var order_lines = [];
//                        for (var i = 0; i < order_lines_value.length; i++) {
//                            order_lines.push(JSON.parse(order_lines_value[i]['data']))
//                        }
//                        pos_order_line_model.loaded(self, order_lines, {});
                        // get qty available filter by stock location id
//                        var params = {
//                            model: 'pos.cache.database',
//                            method: 'get_product_available_filter_by_stock_location_id',
//                            context: {
//                                stock_location_id: self.config.stock_location_id[0],
//                            },
//                            args: [self.config.stock_location_id[0]]
//                        };
                        if (!product_model) {
                            return true;
                        }

                        return $.when(product_model.loaded(self, self.products, {}));

                    } else {
                        if (product_model) { // if old data install pos_cache odoo
                            return $.when(self.load_cache(product_model)).then(function () {
                                return $.when(self.load_cache(partner_model))
                            })
                        } else {
                            return $.when(self.load_cache(product_model)).then(function () {
                                return $.when(self.load_cache(partner_model))

                            })
                        }
                    }
                });
            }).done(function () {
                console.log('Done Load Data.')
            })
        }
    });
});
