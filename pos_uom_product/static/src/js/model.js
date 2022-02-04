odoo.define('pos_uom_product.model', function (require) {
    var models = require('point_of_sale.models');
    var time = require('web.time');
    var utils = require('web.utils');
    var core = require('web.core');
    var round_pr = utils.round_precision;
    var _t = core._t;

    models.load_models([
        {
            model: 'product.uom.price',
            fields: [],
            domain: [],
            context: {'pos': true},
            loaded: function (self, uoms_prices) {
                self.uom_price_by_uom_id = {}
                self.uoms_prices_by_product_tmpl_id = {}
                self.uoms_prices = uoms_prices;
                for (var i = 0; i < uoms_prices.length; i++) {
                    var item = uoms_prices[i];
                    if (item.product_tmpl_id) {
                        self.uom_price_by_uom_id[item.uom_id[0]] = item;
                        if (!self.uoms_prices_by_product_tmpl_id[item.product_tmpl_id[0]]) {
                            self.uoms_prices_by_product_tmpl_id[item.product_tmpl_id[0]] = [item]
                        } else {
                            self.uoms_prices_by_product_tmpl_id[item.product_tmpl_id[0]].push(item)
                        }
                    }
                }
            }
        },
    ]);




});
