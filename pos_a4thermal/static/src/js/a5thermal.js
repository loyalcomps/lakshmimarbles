odoo.define('pos_orders.pos_orders',function(require){
	"use strict"
	var Model = require('web.DataModel');
	var screens = require('point_of_sale.screens');
	var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var utils = require('web.utils');
	var core = require('web.core');
	var QWeb = core.qweb;
	var SuperPosModel = models.PosModel.prototype;
	var _t = core._t;


	var _modelproto = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({

        initialize: function() {
            _modelproto.initialize.apply(this,arguments);

            this.print_type = 'thermal' ;
        },


        set_print_type: function(name){
            //this.set('salesperson_name', name);
            this.print_type = name;
        },
        get_print_type:function(){

            return this.print_type;
        },
    });


    screens.PaymentScreenWidget.include({


    print_type_change: function(value){
            var self = this;
            self.pos.set_print_type(value);
            },
//    finalize_validation: function(){
//        this._super();
//        var fields = {};
//        this.$('.print_type.detail').each(function(idx,el){
//            fields[el.name] = el.value || false;
//        });
//
//        if (!fields.print_type) {
//            this.gui.show_popup('error',_t( 'Select print type'));
//            return;
//        }
//
//    },
    renderElement: function() {
            var self = this;
            this._super();

            self.$('.detail').change(function(){
                console.log('worked');
//                var type = $(this).data('value');
                console.log(this.value);
//                this.pos.print_type =
               self.print_type_change(this.value);



            });
        },

});
    screens.ReceiptScreenWidget.include({
        render_receipt: function() {
        var order = this.pos.get_order();
        var print_type=this.pos.get_print_type();
        if (print_type==='thermal')
        {
        this.$('.pos-receipt-container').html(QWeb.render('PosTicket',{
                widget:this,
                order: order,
                receipt: order.export_for_printing(),
                orderlines: order.get_orderlines(),
                paymentlines: order.get_paymentlines(),
            }));
           this.pos.set_print_type(print_type);
        }
        else{
        this.$('.pos-receipt-container').html(QWeb.render('PosTicketA4',{
                widget:this,
                order: order,
                receipt: order.export_for_printing(),
                orderlines: order.get_orderlines(),
                paymentlines: order.get_paymentlines(),
            }));
            print_type='thermal'
          this.pos.set_print_type(print_type);

        }

    },
    });
});