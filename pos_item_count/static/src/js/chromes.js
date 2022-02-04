odoo.define('pos_item_count.chromes', function (require) {
    "use strict";

    var chrome = require('point_of_sale.chrome');
    var core = require('web.core');
    var _t = core._t;



    var CountItemWidget = chrome.StatusWidget.extend({
        template: 'CountItemWidget',


        set_count_item: function (count) {
            this.$('.count_item').html(count);
        },
        start: function () {
            var self = this;
            this.pos.bind('change:selectedOrder', function () {
                var selectedOrder = self.pos.get_order();
                if (selectedOrder) {

                    self.set_count_item(selectedOrder.orderlines.length)

                }

            });
            this.pos.bind('update:count_item', function () {
                var selectedOrder = self.pos.get_order();
                if (selectedOrder) {

                    self.set_count_item(selectedOrder.orderlines.length)

                } else {
                    self.set_count_item(0)

                }

            });
        }
    });
    chrome.Chrome.include({
        build_widgets: function () {
            this.widgets.push(
                {
                    'name': 'count_item_widget',
                    'widget': CountItemWidget,
                    'append': '.pos-branding',
                }
            );
            this._super();
        }
    });


});

odoo.define('pos_item_count.order', function (require) {

//    var utils = require('web.utils');
//    var round_pr = utils.round_precision;
    var models = require('point_of_sale.models');
//    var core = require('web.core');
//    var _t = core._t;
//    var qweb = core.qweb;


    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            var self = this;
            _super_Order.initialize.apply(this, arguments);
            this.orderlines.bind('change add remove', function (line) {
                self.pos.trigger('update:count_item')
            });
        }
    });


});
