odoo.define('pos_roundoff.Roundoff',function(require){
    "use strict";
    var pos_model = require('point_of_sale.models');
    var screen = require('point_of_sale.screens');
    var SuperOrder = pos_model.Order.prototype;
    pos_model.load_fields('account.journal', ['type', 'sequence', 'visible_in_pos', 'allow_rounding', 'decimal_rounding', 'used_for_rounding']);


    pos_model.Order = pos_model.Order.extend({
        initialize: function(attributes, options) {
            var self = this;
            this.previous_amount = 0;
            SuperOrder.initialize.call(this, attributes, options);
        },
    });

    screen.PaymentScreenWidget.include({
        init: function(parent, options) {
            this.rounding_journal_id = null;
            this._super(parent, options);
        },
        show: function(){
            var self = this;
            self._super();
            self.$('.refresh-button').on('click',function(event){
                self.update_rounding_amount($(this).data('cid'));
            });
        },
        update_rounding_amount: function(cid){
            var self = this;
            self.click_paymentline(cid);
            var current_order =  self.pos.get_order();
            var total_amount = current_order.get_total_with_tax();
            var rounding_amount = self.get_rounding_amount(total_amount);
            current_order.previous_amount = current_order.get_total_with_tax();
            if (rounding_amount != null) {
                current_order.selected_paymentline.set_amount(rounding_amount);
                self.chrome.screens.payment.order_changes();
                self.chrome.screens.payment.render_paymentlines();
                self.chrome.screens.payment.$('.paymentline.selected .edit').text(self.chrome.screens.payment.format_currency_no_symbol(rounding_amount));
            }
        },
        get_rounding_amount: function(total_amount){
            var self = this;
            var selected_paymentline = self.pos.get_order().selected_paymentline;
            var rounding_amount = null;
            if(selected_paymentline){
                var round_value = selected_paymentline.cashregister.journal.decimal_rounding *10;
                var decimal_val = (total_amount - Math.floor(total_amount)).toFixed(2) * 100;
                if(decimal_val<round_value) {

                    rounding_amount = decimal_val/100

                }
                if(decimal_val>round_value) {
                    rounding_amount = (100-decimal_val)*-1
                    rounding_amount = rounding_amount / 100

                }
//                var remainder = decimal_val % round_value;
//                if (round_value > 1) {
//                    if (remainder >= (Math.ceil(round_value / 2))) {
//                        rounding_amount = round_value - remainder;
//                        rounding_amount *= -1;
//                    } else {
//                        rounding_amount = remainder;
//                    }
//                    rounding_amount = rounding_amount / 100
//                }
            }
            return rounding_amount;
        },
        payment_input: function(input){
            var self = this;
            var order = this.pos.get_order();
            if (!(order.selected_paymentline && order.selected_paymentline.cashregister.journal && order.selected_paymentline.cashregister.journal.used_for_rounding))
                self._super(input);
        },
        render_paymentmethods: function() {
            var self = this;
            var self = this;
            var cashregisters = self.pos.cashregisters;
            cashregisters.forEach(function(cashregister) {
                if (cashregister.journal.used_for_rounding)
                    self.rounding_journal_id = cashregister.journal.id;
            });
            return self._super();
        },

        click_paymentmethods: function(id) {
            var self = this;
            var cashregister = null;
            var current_order = self.pos.get_order();
            for (var i = 0; i < this.pos.cashregisters.length; i++) {
                if (this.pos.cashregisters[i].journal_id[0] === id) {
                    cashregister = this.pos.cashregisters[i];
                    break;
                }
            }
            if (cashregister.journal.used_for_rounding) {
                var due = current_order.get_due()
                current_order.add_paymentline(cashregister);
                current_order.previous_amount = current_order.get_total_with_tax();
                var rounding_amount = self.get_rounding_amount(due);
                if (rounding_amount != null) {

                    self.reset_input();
                    self.render_paymentlines();
                    current_order.selected_paymentline.set_amount(rounding_amount);
                    self.chrome.screens.payment.order_changes();
                    self.chrome.screens.payment.render_paymentlines();
                    self.chrome.screens.payment.$('.paymentline.selected .edit').text(self.chrome.screens.payment.format_currency_no_symbol(rounding_amount));
                    self.$('.refresh-button').hide();
                }
            } else {
                if ((cashregister.journal.allow_rounding) && self.rounding_journal_id && !self.check_rounding_paymentline()) {
                    self.chrome.screens.payment.click_paymentmethods(self.rounding_journal_id);
                }
                self._super(id);
            }
        },
        check_rounding_paymentline: function(){
            var self = this;
            var current_order = self.pos.get_order();
            var paymentlines = current_order.get_paymentlines();
            var is_rounding_paymentline = false;
            paymentlines.forEach(function(line){
                if(line.cashregister.journal.id == self.rounding_journal_id){
                    is_rounding_paymentline = line;
                    return true;
                }
            });
             return is_rounding_paymentline;
             }
    });

});
