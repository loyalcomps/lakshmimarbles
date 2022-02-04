/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('wk_pos_partial_payment.screens', function (require) {
    "use strict";

    var screens = require("point_of_sale.screens");
    var core = require('web.core');
    var _t = core._t;

    screens.PaymentScreenWidget.include({
        events : _.extend({}, screens.PaymentScreenWidget.prototype.events, {
            'focusin #partial_payment_description': 'focus_in_description',
            'focusout #partial_payment_description': 'focus_out_description',
            'keyup #partial_payment_description': 'keyup_description',
        }),
        show: function(){
            this._super();
            var order = this.pos.get_order();
            if(order && order.get_total_with_tax() > 0)
                $('.partial-payment-remark').show();
            else
                $('.partial-payment-remark').hide();
            this.check_partial_payment_criteria();
        },
        focus_in_description: function(event){
            var self = this;
            window.document.body.removeEventListener('keypress',self.keyboard_handler);
            window.document.body.removeEventListener('keydown',self.keyboard_keydown_handler);
        },
        focus_out_description: function(event){
            var self = this;
            window.document.body.addEventListener('keypress',self.keyboard_handler);
            window.document.body.addEventListener('keydown',self.keyboard_keydown_handler);
        },
        keyup_description: function(event){
            this.check_partial_payment_criteria();
        },
        check_partial_payment_criteria: function(){
            var self = this;
            var $elvalidate = $('.next');
            var order = self.pos.get_order();
            var client = order.get_client();
            if(!self.pos.config.partial_payment)
                $elvalidate.removeClass('highlight');
            else if(client != null && order.get_due()>0 && order.is_to_invoice() && self.$('#partial_payment_description').val()!=''){
                if(client.property_payment_term_id && !client.prevent_partial_payment)
                    $elvalidate.addClass('highlight');
                else
                    $elvalidate.removeClass('highlight');
            }
            else if(order.is_to_invoice() && self.$('#partial_payment_description').val()=='')
                $elvalidate.removeClass('highlight');
            else if(order.get_due() != 0)
                $elvalidate.removeClass('highlight');
            else if(order.get_due() == 0 && order.get_total_with_tax() != 0)
                $elvalidate.addClass('highlight');
        },
        click_invoice: function(){
            this._super();
            this.check_partial_payment_criteria();
        },
        validate_order: function(force_validation) {
            var self = this;
            var order = self.pos.get_order();
            if (!self.pos.config.partial_payment)
                this._super(force_validation);
            else{
                order.invoice_remark = self.$('#partial_payment_description').val();
                if (order.get_orderlines().length === 0) {
                    this.gui.show_popup('error',{
                        'title': _t('Empty Order'),
                        'body':  _t('There must be at least one product in your order before it can be validated'),
                    });
                    return false;
                }
                else if (!this.order_is_valid(force_validation)) {
                    if(!order.is_paid() && !order.is_to_invoice()){
                        self.gui.show_popup('partial_payment_block',{
                            'title': _t('Cannot Validate This Order!!!'),
                            'body':  _t("You need to set Invoice for validating Partial Payments."),
                        });
                        return;
                    }if (order.is_to_invoice()) {
                        if(order.get_client() != null && order.get_due()>0){
                            if(order.get_client().prevent_partial_payment){
                                self.gui.show_popup('partial_payment_block',{
                                    'title': _t('Cannot Validate This Order!!!'),
                                    'body':  _t("Customer's Payment Term does not allow Partial Payments."),
                                });
                                return false;
                            }
                        }if(self.$('#partial_payment_description').val()==''){
                            self.$("#partial_payment_description").css("background-color","burlywood");
                            setTimeout(function(){
                                self.$("#partial_payment_description").css("background-color","");
                            },100);
                            setTimeout(function(){
                                self.$("#partial_payment_description").css("background-color","burlywood");
                            },200);
                            setTimeout(function(){
                                self.$("#partial_payment_description").css("background-color","");
                            },300);
                            setTimeout(function(){
                                self.$("#partial_payment_description").css("background-color","burlywood");
                            },400);
                            setTimeout(function(){
                                self.$("#partial_payment_description").css("background-color","");
                            },500);
                            return;
                        }
                    }
                    order.is_partially_paid = true;
                    this.finalize_validation();
                }else
                    this.finalize_validation();
            }
        },
    });
});
