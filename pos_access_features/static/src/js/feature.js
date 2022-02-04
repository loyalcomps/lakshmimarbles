odoo.define('pos_access_features.feature', function (require){
"use strict"

var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var _t = core._t;
	var gui = require('point_of_sale.gui');
	var popup_widget = require('point_of_sale.popups');
	var SuperPaymentScreenWidget = screens.PaymentScreenWidget.prototype;

//
//	screens.PaymentScreenWidget.include({
//		finalize_validation: function() {
//			var self = this;
//			var order = self.pos.get_order();
//			if (self.pos.config.validation_check)
//			{
//				if(order.get_client()==null)
//				{
//					self.gui.show_popup('confirm',{
//						'title': _t('Please Select The Customer'),
//						'body': _t('You need to select the customer before you can validate the order.'),
//						confirm: function(){
//							self.gui.show_screen('clientlist');
//						},
//					});
//				}else
//					this._super();
//			}else
//				this._super();
//		},
//	});
//
//	var PriceUpdatePopupWidget = popup_widget.extend({
//		template:'PriceUpdatePopupWidget',
//
//
//		show: function(options){
//			var self = this;
//			this._super(options);
//			$('#price_input').keyup(function(){
//				if (event.keyCode === 13)
//					$('#wk_ok').trigger('click');
//
//			});
//
//		},
//		events: {
//			'click #wk_ok':'click_ok',
//			'click #wk_cancel': 'click_cancel',
//		},
//
//		click_ok: function(){
//			var self = this;
//			var previous_price = self.pos.get_order().selected_orderline.price;
//			var new_price = $("#price_input").val();
//			if(!$.isNumeric(new_price))
//			{
//				$('#price_error').show();
//				$('#price_error').addClass("fa fa-warning");
//				$('#price_error').text("  Please enter a numeric value");
//			}
//			else if(parseFloat(new_price)<parseFloat(previous_price))
//			{
//				$('#price_error').show();
//				$('#price_error').addClass("fa fa-warning");
//				$('#price_error').text("  New price must be greater than current price!!");
//			}
//			else
//			{
//				self.pos.gui.current_screen.order_widget.numpad_state.appendNewChar(new_price);
//				self.gui.close_popup();
//				self.pos.gui.current_screen.order_widget.numpad_state.reset();
//			}
//		},
//		click_cancel:function(){
//			var self=this;
//			self.pos.gui.current_screen.order_widget.numpad_state.reset();
//			self.gui.close_popup();
//		},
//
//	});
//	gui.define_popup({name:'price_update', widget: PriceUpdatePopupWidget});

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
            var self = this;
            var user = this.pos.cashier || this.pos.user;
            var order = this.pos.get_order();
            var orderline = false;
            if (order) {
                orderline = order.get_selected_orderline();
            }
            if (!self.pos.config.disable_discount) {
                this.$el.find("[data-mode='discount']").removeClass('disable');
            }else{
                this.$el.find("[data-mode='discount']").addClass('disable');
            }

            if (!self.pos.config.disable_price) {
                this.$el.find("[data-mode='price']").removeClass('disable');
//                this.$el.find("[data-mode='price']").addClass('oe_hidden');

            }else{
                this.$el.find("[data-mode='price']").addClass('disable');
            }

        },


//		changedMode: function() {
//			var self = this;
//			var mode = this.state.get('mode');
//			$('.selected-mode').removeClass('selected-mode');
//			$(_.str.sprintf('.mode-button[data-mode="%s"]', mode), this.$el).addClass('selected-mode');
//
//		},
//		clickChangeMode: function(event) {
//			var self = this;
//			var previous_mode = $('.selected-mode').attr('data-mode');
//			var newMode = event.currentTarget.attributes['data-mode'].nodeValue;
//			if(self.pos.config.disable_price && newMode=='price')
//					newMode =previous_mode;
//			if(self.pos.config.disable_discount && newMode=='discount')
//					newMode =previous_mode;
//			return this.state.changeMode(newMode);
//		},
//		clickDeleteLastChar: function() {
//			var self = this;
//			var selected_mode = $('.selected-mode').attr('data-mode');
//			if(!self.pos.config.disable_delete_button || selected_mode == 'quantity')
//				return this.state.deleteLastChar();
//		},
	});
});
