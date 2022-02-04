odoo.define('qlty_product_available.PosModel', function(require){
"use strict";

var utils = require('web.utils');

var round_di = utils.round_decimals;
var round_pr = utils.round_precision;


    var models = require('point_of_sale.models');
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function(model){ return model.model === 'product.product'; });
            partner_model.fields.push('product_mrp');
            
            return _super_posmodel.initialize.call(this, session, attributes);
        },
    });

    var PosModelSuper = models.PosModel;

    models.PosModel = models.PosModel.extend({
        refresh_qty_available:function(product){
            var $elem = $("[data-product-id='"+product.id+"'] .qty-tag");
            $elem.html(product.product_mrp);
            if (product.product_mrp <= 0 && !$elem.hasClass('not-available')){
                $elem.addClass('not-available');
            }
        },
        push_order: function(order, opts){
            var self = this;
            var pushed = PosModelSuper.prototype.push_order.call(this, order, opts);
            if (order){
                order.orderlines.each(function(line){
                    var product = line.get_product();
//                    product.qty_available -= line.get_quantity();
                    self.refresh_qty_available(product);
                });
            }
            return pushed;
        },
        push_and_invoice_order: function(order){
            var self = this;
            var invoiced = PosModelSuper.prototype.push_and_invoice_order.call(this, order);

            if (order && order.get_client()){
                if (order.orderlines){
                    order.orderlines.each(function(line){
                        var product = line.get_product();
//                        product.qty_available -= line.get_quantity();
                        self.refresh_qty_available(product);
                    });
                } else if (order.orderlines){
                    order.orderlines.each(function(line){
                        var product = line.get_product();
//                        product.qty_available -= line.get_quantity();
                        self.refresh_qty_available(product);
                    });
                }
            }

            return invoiced;
        },
    });
    var _super_order = models.Order.prototype;

    models.Order = models.Order.extend({

      get_total_with_mrp: function() {
         var total_mrp=0;
          this.orderlines.each(function(line){
               total_mrp += line.get_product().product_mrp * line.get_quantity();
          });
          return Math.round(total_mrp);
        },



        get_tax_details_qlty: function(){
            var details = {};
            var taxwithout={};
            var fulldetails = [];

            this.orderlines.each(function(line){
                var ldetails = line.get_tax_details();
                var tax_without = line.get_price_without_tax();
                for(var id in ldetails){
                    if(ldetails.hasOwnProperty(id)){
                        details[id] = (details[id] || 0) + ldetails[id];
                        taxwithout[id] = (parseFloat((taxwithout[id] || 0)) + tax_without).toFixed(2);
                    }
                }
            });

            for(var id in details){
                if(details.hasOwnProperty(id)){
                    fulldetails.push({amount: details[id], tax: this.pos.taxes_by_id[id],taxable: taxwithout[id] , name: this.pos.taxes_by_id[id].name});
                }
            }

            return fulldetails;
        },

        add_product: function (product, options) {
            var res = _super_order.add_product.apply(this, arguments);
            var selected_orderline = this.selected_orderline;
            options = options || {};
            if(options.product_mrp !== undefined){
                selected_orderline['product_mrp'] = options.product_mrp;
                selected_orderline.trigger('change', selected_orderline);
            }


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
        this.product_mrp = options.product.product_mrp;
    },
    set_product_mrp: function(product_mrp){
        this.product_mrp = product_mrp;
    },
    get_product_mrp: function(product_mrp){
        return this.product_mrp;
    },
    get_product_mrp_print: function(){
        var digits = this.pos.dp['Product Price'];
        // round and truncate to mimic _sybmbol_set behavior
        return parseFloat(round_di(this.product_mrp || 0, digits).toFixed(digits));
    },

    clone: function(){
        var orderline = _super_orderline.clone.call(this);
        orderline.product_mrp = this.product_mrp;
        return orderline;
    },
    export_as_JSON: function(){
        var json = _super_orderline.export_as_JSON.call(this);
        json.product_mrp = this.product_mrp;
        return json;
    },
    init_from_JSON: function(json){
        _super_orderline.init_from_JSON.apply(this,arguments);
        this.product_mrp = json.product_mrp;
    },

    export_for_printing: function() {
        var json = _super_orderline.export_for_printing.apply(this,arguments);
        json.product_mrp = this.product_mrp;
        return json;
    },
});










});
