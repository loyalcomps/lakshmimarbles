odoo.define('pos_access_right.pos_access_rigtht', function(require){

"use strict";

    var chrome = require('point_of_sale.chrome');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var _t = core._t;

    models.load_fields("res.users", ['allow_discount','allow_edit_price','cash_discount','pos_discount',]);

    // Example of event binding and handling (triggering). Look up binding lower bind('change:cashier' ...
    // Example extending of class (method set_cashier), than was created using extend.
    // /odoo9/addons/point_of_sale/static/src/js/models.js
    // exports.PosModel = Backbone.Model.extend ...
    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        set_cashier: function(){
            var old_cashier_id = this.db.get_cashier() && this.db.get_cashier().id;
            PosModelSuper.prototype.set_cashier.apply(this, arguments);
            if (old_cashier_id !== this.db.get_cashier().id) {
                this.trigger('change:cashier', this);
            }
        }
    });


    // Here regular binding (in init) do not work for some reasons. We got to put binding method in renderElement.
    screens.ProductScreenWidget.include({
        start: function () {
            this._super();

            this.checkDiscountButton();
        },
        renderElement: function () {
            this._super();

            this.pos.bind('change:cashier', this.checkDiscountButton, this);
        },



        checkDiscountButton: function() {
            var user = this.pos.get_cashier() || this.pos.user;
            if (user.pos_discount) {
                $('.control-button.js_discount').removeClass('disable');
            }else{
                $('.control-button.js_discount').addClass('disable');
            }

            if (user.cash_discount) {
                $('#cash_disc').removeClass('disable');
            }else{
                $('#cash_disc').addClass('disable');
            }

        },


    });



    screens.NumpadWidget.include({
        init: function () {
            this._super.apply(this, arguments);
            this.pos.bind('change:cashier', this.check_access, this);
        },
        renderElement: function(){
            this._super();
            this.check_access();
        },
        check_access: function(){
            var user = this.pos.get_cashier() || this.pos.user;
            var order = this.pos.get_order();
            var orderline = false;
            if (order) {
                orderline = order.get_selected_orderline();
            }
            if (user.allow_discount) {
                this.$el.find("[data-mode='discount']").removeClass('disable');
            }else{
                this.$el.find("[data-mode='discount']").addClass('disable');
            }
            if (user.allow_edit_price) {
                this.$el.find("[data-mode='price']").removeClass('disable');
            }else{
                this.$el.find("[data-mode='price']").addClass('disable');
            }

//            if (user.pos_discount) {
//                $('#pos_disc').removeClass('disable');
//            }else{
//                $('#pos_disc').addClass('disable');
//            }
//
//            if (user.cash_discount) {
//                $('#cash_disc').removeClass('disable');
//            }else{
//                $('#cash_disc').addClass('disable');
//            }


//
//            if (user.pos_discount) {
//                this.$el.find("#pos_disc").removeClass('disable');
//            }else{
//                this.$el.find("#pos_disc").addClass('disable');
//            }
//
//            if (user.cash_discount) {
//                this.$el.find("#cash_disc").removeClass('disable');
//            }else{
//                this.$el.find("#cash_disc").addClass('disable');
//            }



        }
    });
});