odoo.define('pos_bulk_load.model', function (require) {
    var models = require('point_of_sale.models');
    var time = require('web.time');
    var utils = require('web.utils');
    var core = require('web.core');
    var round_pr = utils.round_precision;
    var _t = core._t;
    var rpc = require('web.rpc');
    var big_data = require('pos_bulk_load.bulk');

    var _super_PosModel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({

        // thay doi thong tin san pham
        syncing_product: function (product_data) {
            var self = this;
            this.trigger('product:updated', product_data)

        },
        syncing_partner: function (customer_data) {
            this.trigger('update:customer_screen', customer_data);
        },
        // thay doi items cua pricelist
//        syncing_pricelist: function (pricelist_data) {
//            if (this.default_pricelist && this.default_pricelist['id'] == pricelist_data['id']) {
//                pricelist_data['items'] = this.default_pricelist['items']
//                this.default_pricelist = pricelist_data;
//            }
//            if (this.pricelists) {
//                for (var i = 0; i < this.pricelists.length; i++) {
//                    if (this.pricelists[i]['id'] == pricelist_data['id']) {
//                        pricelist_data['items'] = this.pricelists[i]['items']
//                        this.pricelists[i] = pricelist_data;
//                    }
//                }
//            }
//        },
        // thay doi items cua pricelist
//        syncing_pricelist_item: function (pricelist_item) {
//            var pricelist_by_id = {};
//            _.each(this.pricelists, function (pricelist) {
//                pricelist_by_id[pricelist.id] = pricelist;
//            });
//            var pricelist = pricelist_by_id[pricelist_item.pricelist_id[0]];
//            if (pricelist) {
//                var append_items = false;
//                for (var i = 0; i < pricelist.items.length; i++) {
//                    if (pricelist.items[i]['id'] == pricelist_item['id']) {
//                        pricelist.items[i] = pricelist_item;
//                        append_items = true
//                    }
//                }
//                if (append_items == false) {
//                    pricelist.items.push(pricelist_item);
//                }
//            }
//        },
    });
});
