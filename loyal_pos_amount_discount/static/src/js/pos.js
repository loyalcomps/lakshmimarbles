odoo.define('loyal_pos_amount_discount.PosModel', function(require){
"use strict";

    var models = require('point_of_sale.models');
    var _super_posmodel = models.PosModel.prototype;
    var _super_orderline = models.Orderline.prototype;


    models.Orderline = models.Orderline.extend({

     set_discount: function(discount){
        var disc = Math.min(Math.max(parseFloat(discount) || 0, 0),10000);
        this.discount = disc;
        this.discountStr = '' + disc;
        this.trigger('change',this);
    },

     get_base_price:    function(){
        var rounding = this.pos.currency.rounding;
        return ((this.get_unit_price() * this.get_quantity()) - this.get_discount());
    },

     get_all_prices: function(){
        var price_unit =  (((this.get_unit_price() * this.get_quantity()) - this.get_discount())/this.get_quantity());
        var taxtotal = 0;
        var product =  this.get_product();
        var taxes_ids = product.taxes_id;
        var taxes =  this.pos.taxes;
        var taxdetail = {};
        var product_taxes = [];

        _(taxes_ids).each(function(el){
            product_taxes.push(_.detect(taxes, function(t){
                return t.id === el;
            }));
        });

        var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
        _(all_taxes.taxes).each(function(tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = tax.amount;
        });

        return {
            "priceWithTax": all_taxes.total_included,
            "priceWithoutTax": all_taxes.total_excluded,
            "tax": taxtotal,
            "taxDetails": taxdetail,
        };
    },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({


    get_total_discount: function() {
        return this.orderlines.reduce((function(sum, orderLine) {
            return sum + (orderLine.get_discount()) ;
        }), 0) ;
    },


    });

});