odoo.define('pos_price_edit_log.ProductPriceLog', function(require){
    "use strict";

    var utils = require('web.utils');

    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;


    var models = require('point_of_sale.models');

    var PosModelSuper = models.PosModel;

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({

        add_product: function (product, options) {
            var res = _super_order.add_product.apply(this, arguments);
            var selected_orderline = this.selected_orderline;
            options = options || {};

            if(options.barcode_id){
                selected_orderline['actual_price'] = options.price;
                selected_orderline.trigger('change', selected_orderline);
            }
            else{
                selected_orderline['actual_price'] = product.list_price;
                selected_orderline.trigger('change', selected_orderline);
            }
//            else{
//                selected_orderline['actual_price'] = 0;
//                selected_orderline.trigger('change', selected_orderline);
//            }


            return res
        },

    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
            _super_orderline.initialize.call(this,attr,options);
            if (options.json) {
                this.init_from_JSON(options.json);
                return;
            }
            this.actual_price = options.product.list_price;
        },
        set_product_actual_price: function(actual_price){
            this.actual_price = actual_price;
        },
        get_product_actual_price: function(actual_price){
            return this.actual_price;
        },
        clone: function(){
            var orderline = _super_orderline.clone.call(this);
            orderline.actual_price = this.actual_price;
            return orderline;
        },
        export_as_JSON: function(){
            var json = _super_orderline.export_as_JSON.call(this);
            json.actual_price = this.actual_price;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.actual_price = json.actual_price;
        },

        export_for_printing: function() {
            var json = _super_orderline.export_for_printing.apply(this,arguments);
            json.actual_price = this.actual_price;
            return json;
        },
    });

});
