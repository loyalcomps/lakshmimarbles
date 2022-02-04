odoo.define('pos_extra_utilities.pos_extra_utilities', function (require) {
"use strict";
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var _t = core._t;
	var gui = require('point_of_sale.gui');
	var popup_widget = require('point_of_sale.popups');
	var SuperPaymentScreenWidget = screens.PaymentScreenWidget.prototype;


	screens.PaymentScreenWidget.include({
		finalize_validation: function() {
			var self = this;
			var order = self.pos.get_order();
			if (self.pos.config.validation_check)
			{
				if(order.get_client()==null)
				{
					self.gui.show_popup('confirm',{
						'title': _t('Please Select The Customer'),
						'body': _t('You need to select the customer before you can validate the order.'),
						confirm: function(){
							self.gui.show_screen('clientlist');
						},
					});
				}else
					this._super();
			}else
				this._super();
		},
	});

	var PriceUpdatePopupWidget = popup_widget.extend({
		template:'PriceUpdatePopupWidget',


		show: function(options){
			var self = this;
			this._super(options);
			$('#price_input').keyup(function(){
				if (event.keyCode === 13)
					$('#wk_ok').trigger('click');

			});

		},
		events: {
			'click #wk_ok':'click_ok',
			'click #wk_cancel': 'click_cancel',
		},

		click_ok: function(){
			var self = this;
			var previous_price = self.pos.get_order().selected_orderline.price;
			var new_price = $("#price_input").val();
			if(!$.isNumeric(new_price))
			{
				$('#price_error').show();
				$('#price_error').addClass("fa fa-warning");
				$('#price_error').text("  Please enter a numeric value");
			}
			else if(parseFloat(new_price)<parseFloat(previous_price))
			{
				$('#price_error').show();
				$('#price_error').addClass("fa fa-warning");
				$('#price_error').text("  New price must be greater than current price!!");
			}
			else
			{
				self.pos.gui.current_screen.order_widget.numpad_state.appendNewChar(new_price);
				self.gui.close_popup();
				self.pos.gui.current_screen.order_widget.numpad_state.reset();
			}
		},
		click_cancel:function(){
			var self=this;
			self.pos.gui.current_screen.order_widget.numpad_state.reset();
			self.gui.close_popup();
		},

	});
	gui.define_popup({name:'price_update', widget: PriceUpdatePopupWidget});

	screens.NumpadWidget.include({
		changedMode: function() {
			var self = this;
			var mode = this.state.get('mode');
			$('.selected-mode').removeClass('selected-mode');
			$(_.str.sprintf('.mode-button[data-mode="%s"]', mode), this.$el).addClass('selected-mode');
			if(self.pos.config.allow_only_price_increase && mode == 'price')
			{
				if(self.pos.get_order().selected_orderline){
					self.gui.show_popup('price_update',{});
					$("#price_input").val(self.pos.get_order().selected_orderline.price);
					$('#price_input').focus();
				}

			}
		},
		clickChangeMode: function(event) {
			var self = this;
			var previous_mode = $('.selected-mode').attr('data-mode');
			var newMode = event.currentTarget.attributes['data-mode'].nodeValue;
			if(self.pos.config.disable_price_modification && newMode=='price')
					newMode =previous_mode;
			if(self.pos.config.disable_discount_button && newMode=='discount')
					newMode =previous_mode;
			return this.state.changeMode(newMode);
		},
		clickDeleteLastChar: function() {
			var self = this;
			var selected_mode = $('.selected-mode').attr('data-mode');
			if(!self.pos.config.disable_delete_button || selected_mode == 'quantity')
				return this.state.deleteLastChar();
		},
	});
});