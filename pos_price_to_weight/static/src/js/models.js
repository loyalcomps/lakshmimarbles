odoo.define('pos_price_to_weight.models', function (require) {
    "use strict";


    var models = require('point_of_sale.models');

    var exports = {};

    var _super_PosModel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({

        scan_product: function(parsed_code) {
            if (!(parsed_code.type === 'price_to_weight' || parsed_code.type === 'price_to_piece'))  {
                // Normal behaviour
                return _super_PosModel.scan_product.apply(this, [parsed_code]);
            }
            var selectedOrder = this.get_order();
            var str = parsed_code.base_code;
            if (str.length > 11){
                var barcode = str.slice(2, 7);
            }
            else{
                var barcode = str.slice(1, 6);
            }

            var product = this.db.get_product_by_barcode(barcode);
            if(!product){
                return false;
            }
            var quantity = parseFloat(parsed_code.value) || 0;

            selectedOrder.add_product_new(product, {quantity:  quantity, merge: false});
            return true;
        },



    });


    var _super_order = models.Order.prototype;

    models.Order = models.Order.extend({


        add_product_new: function(product, options){
        if(this._printed){
            this.destroy();
            return this.pos.get_order().add_product_new(product, options);
        }
        this.assert_editable();
        options = options || {};
        var attr = JSON.parse(JSON.stringify(product));
        attr.pos = this.pos;
        attr.order = this;
        var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});

        if(options.quantity !== undefined){
            line.set_quantity(options.quantity);
        }

        if(options.price !== undefined){
            line.set_unit_price(options.price);
        }

        console.log('Added QTY '+line.quantity);

        //To substract from the unit price the included taxes mapped by the fiscal position
        this.fix_tax_included_price(line);

        if(options.discount !== undefined){
            line.set_discount(options.discount);
        }

        if(options.extras !== undefined){
            for (var prop in options.extras) {
                line[prop] = options.extras[prop];
            }
        }

        var last_orderline = this.get_last_orderline();
        if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
            last_orderline.merge(line);
        }else{
            this.orderlines.add(line);
        }
        this.select_orderline(this.get_last_orderline());

        if(line.has_product_lot){
            this.display_lot_popup();
        }
    },

    });
});