odoo.define('pos_orderline_payment_restriction.line_payment', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var utils = require('web.utils');
    var Model = require('web.DataModel');

    var QWeb = core.qweb;
    var _t = core._t;
    var round_pr = utils.round_precision;

    var _super_posmodel = models.PosModel.prototype;


    var _super_order = models.Order.prototype;


    screens.ActionpadWidget.include({



        renderElement: function () {
            var self = this;
            var flag = false;
            this._super();
            this.$('.pay').click(function () {
                var order = self.pos.get_order();
                var payment_lines = order.orderlines.models;
                for(var i=0; i<payment_lines.length; i++){


                     if ((payment_lines[i].price*payment_lines[i].quantity)*(1 - (payment_lines[i].discount) / 100.0) == 0)
                     {

                         self.gui.show_popup('confirm',{
                                'title': _t('Order'),
                                'body':  _t('Zero amount in orderline. Do you want to delete orderline?'),
                                confirm: function(){
                                    self.gui.show_screen('products');
                                },
                            });
//                         alert("Zero Amount in Orderline")
//                         self.gui.show_screen('products');
                         flag = true;
                         break;
                     }
                     if(flag==false){

                        var order = self.pos.get_order();
                        var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                            return line.has_valid_product_lot();
                        });
                        if(!has_valid_product_lot){
                            self.gui.show_popup('confirm',{
                                'title': _t('Empty Serial/Lot Number'),
                                'body':  _t('One or more product(s) required serial/lot number.'),
                                confirm: function(){
                                    self.gui.show_screen('payment');
                                },
                            });
                        }else{
                            self.gui.show_screen('payment');
                        }


                     }



                }


            });
        }
    });





});