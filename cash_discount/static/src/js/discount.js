odoo.define('cash_discount.cash_discount', function (require) {
"use strict";

var screens = require('point_of_sale.screens');

var cashDiscountButton = screens.ActionButtonWidget.extend({
    template: 'cashDiscountButton',
    button_click: function(){
        var self = this;
        this.gui.show_popup('number',{
            'title': 'Discount Cash',
            'value': this.pos.config.discount_pc,
            'confirm': function(val) {
                //val = Math.round(Math.max(0,Math.min(100,val)));
                val = Math.max(0,Math.min(2000,val));

                self.apply_discount(val);
            },
        });
    },
    apply_discount: function(pc) {
        var order    = this.pos.get_order();
        var lines    = order.get_orderlines();
        var product  = this.pos.db.get_product_by_id(this.pos.config.discount_product_id[0]);

        // Remove existing discounts
        var i = 0;
        while ( i < lines.length ) {
            if (lines[i].get_product() === product) {
                order.remove_orderline(lines[i]);
            } else {
                i++;
            }
        }

        // Add discount
         //var discount = - pc / 100.0 * order.get_total_with_tax();
       var discount = - pc;

        if( discount < 0 ){
            order.add_product(product, { price: discount });
        }
    },
});

screens.define_action_button({
    'name': 'discount',
    'widget': cashDiscountButton,
    'condition': function(){
        return this.pos.config.iface_discount_cash && this.pos.config.discount_product_id_cash;
    },
});


});
