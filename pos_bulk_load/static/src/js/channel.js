odoo.define('pos_bulk_load.pos_chanel', function (require) {
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var exports = {};
    var Backbone = window.Backbone;
    var bus = require('bus.bus');
    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;

    // chanel 1: pos.stock.update

    // chanel 2: pos sync backend
    // lien ket qua file pos sync data
    exports.sync_backend = Backbone.Model.extend({
        initialize: function (pos) {
            this.pos = pos;
        },
        start: function () {
            this.bus = bus.bus;
            this.bus.last = this.pos.db.load('bus_last', 0);
            this.bus.on("notification", this, this.on_notification);
            this.bus.start_polling();
        },
        on_notification: function (notifications) {
            if (notifications && notifications[0] && notifications[0][1]) {
                for (var i = 0; i < notifications.length; i++) {
                    var channel = notifications[i][0][1];
                    if (channel == 'pos.sync.data') {
                        this.on_notification_do(notifications[i][1]);
                    }
                }
            }
        },
        on_notification_do: function (datas) {
            var model = datas['model'];
            if (model == 'product.product') {
                this.pos.syncing_product(datas)
            }
            if (model == 'res.partner') {
                this.pos.syncing_partner(datas)
            }
//            if (model == 'product.pricelist' && this.pos.config.sync_pricelist == true) {
//                this.pos.syncing_pricelist(datas)
//            }
//            if (model == 'product.pricelist.item' && this.pos.config.sync_pricelist == true) {
//                this.pos.syncing_pricelist_item(datas)
//            }
        }
    });


    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        load_server_data: function () {
            var self = this;
            // create variable for loaded can load this variable
            // this.products = [];
            return _super_posmodel.load_server_data.apply(this, arguments).then(function () {
                // 1. bus active sync product
//                if (self.config.sync_product || self.config.sync_customer) {
                    self.chrome.loading_message(_t('Active sync data'), 1);
                    self.sync_backend = new exports.sync_backend(self);
                    self.sync_backend.start();
//                }


            }).done(function () {
                console.log('load_server_data DONE');
            })
        }
    });
    return exports;
});
