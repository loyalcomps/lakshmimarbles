odoo.define('pos_customer_pricelist.pos_customer_pricelist', function(require) {
	"use strict";

	var pos_model = require('point_of_sale.models');
	var Model = require('web.DataModel');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var _t = core._t;
	var gui = require('point_of_sale.gui');
	var PopupWidget = require("point_of_sale.popups");
	var model_list = pos_model.PosModel.prototype.models;
	var SuperOrder = pos_model.Order.prototype;
	var product_model = null;
	pos_model.load_fields('res.partner', ['property_product_pricelist']);

	
	// --Fetching model dictionaries--
	for(var i = 0,len = model_list.length;i<len;i++){
		if(model_list[i].model == "product.product"){
			product_model = model_list[i];
			break;
		}
	}

	//--Updating model dictionaries--
	var super_product_loaded = product_model.loaded;
	product_model.loaded = function(self, products){
		self.all_products_ids = [];
		self.all_products = products;
		products.forEach(function(product) {
			self.all_products_ids.push(product.id);
		});
		super_product_loaded.call(this,self,products);
		$.blockUI({ message: '<h1 style="color: #c9d0d6;"><i class="fa fa-lock"></i> Screen Locked...</h1><center><p style="color: #f0f8ff;">Loading Pricelist Information..</p></center>' });
		new Model('product.product').call('get_price_by_pricelist', [{ 'product_ids': self.all_products_ids, 'currency_id': self.currency.id }])
		.then(function(price_dictionary) {
			self.db.price_dict = price_dictionary;
			$.unblockUI();
			if(self.chrome.screens)
			    {
			        var order = self.gui.pos.get_order();
			        if(order){
			            self.gui.pos.get_order().change_pricelist();
			        }

			    }
//				self.gui.pos.get_order().change_pricelist();
		});
	};

	//--Loading Pricelists--
	pos_model.load_models({
		model: 'product.pricelist',
		fields: ['name', 'id', 'currency_id'],
		domain: function(self) {
			return [['currency_id', '=', self.currency.id]];
		},
		loaded: function(self, pricelists) {
			var pos_default_pricelist_id = self.config.pricelist_id[0];
			self.db.pricelist_by_id = {};
			pricelists.forEach(function(pricelist) {
				self.db.pricelist_by_id[pricelist.id] = pricelist;
				if (pricelist.id == pos_default_pricelist_id) {
					self.pricelist = pricelist;
					self.db.pos_default_pricelist = pricelist;
				}
			});
			self.pricelists = pricelists;
		},
	});

	//--Custom Message Popup--
	var CustomerPricelistInfoPopup = PopupWidget.extend({
		template: 'CustomerPricelistInfoPopup',
	});
	gui.define_popup({ name: 'pos_customer_pricelist_custom_message', widget: CustomerPricelistInfoPopup });

	//Order Model
	pos_model.Order = pos_model.Order.extend({
		init_from_JSON: function(json) {
			var self = this;
			SuperOrder.init_from_JSON.call(this,json);
			if(json.pricelist_id)
				self.order_pricelist = self.pos.db.pricelist_by_id[json.pricelist_id];
		},
		initialize: function(attributes, options) {
			self = this;
			SuperOrder.initialize.call(this, attributes, options);
			this.need_to_remove_orderlines = false;
			var pos_default_pricelist_id = self.pos.config.pricelist_id[0];
			if (options.json){
				if(options.json.pricelist_id == null){
					self.order_pricelist = self.pos.db.pricelist_by_id[pos_default_pricelist_id];
					self.pricelist = self.pos.db.pricelist_by_id[pos_default_pricelist_id];
				}
			}
			else{
				self.order_pricelist = self.pos.db.pricelist_by_id[pos_default_pricelist_id];
				self.pricelist = self.pos.db.pricelist_by_id[pos_default_pricelist_id];
			}
		},
		export_as_JSON: function() {
			var self = this;
			var loaded = SuperOrder.export_as_JSON.call(this);
			if (self.pos.get_order())
				loaded.pricelist_id = self.pos.get_order().order_pricelist.id;
			return loaded;
		},

		//--Custom--Checks if the order contains orderlines of some other pricelist
		check_remove_lines: function(client){
			var self = this;
			var current_pricelist_id = self.order_pricelist.id;
			var new_pricelist_id;
			if(self && self.orderlines.length == 0)
				self.need_to_remove_orderlines = false;
			else{
				if(client != null)
					new_pricelist_id = client.property_product_pricelist[0]
				else
					new_pricelist_id = self.pos.db.pos_default_pricelist.id
				if(current_pricelist_id == new_pricelist_id)
					self.need_to_remove_orderlines = false;
				else
					self.need_to_remove_orderlines = true;
			}
		},

		//--Sets the pricelist depending on the new customer--
		set_client: function(client) {
			var self = this;
			var current_pricelist = self.order_pricelist;
			var customer_pricelist_id;
			if (self.pos.db.price_dict != null && self.pos.chrome.screens != null) {
//				self.check_remove_lines(client)
				SuperOrder.set_client.call(this, client);
				if (client != null) {
					customer_pricelist_id = client.property_product_pricelist[0];
					if (current_pricelist.id != customer_pricelist_id) {
						if(self.pos.db.pricelist_by_id[customer_pricelist_id]){
							self.order_pricelist = self.pos.db.pricelist_by_id[customer_pricelist_id]
							self.change_pricelist();
						}
					}
				} else {
					self.order_pricelist = self.pos.db.pos_default_pricelist
					self.change_pricelist();
				}
			}
			else
				SuperOrder.set_client.call(this, client);
		},

		//--Custom--Sets product prices base on the Order Pricelist
		change_pricelist: function() {
			var self = this;
			var product_id;
			var product_price_for_pricelst;
			var formatted_price;
			var order_pricelist = self.order_pricelist;
			self.pos.pricelist = order_pricelist;
//			$('div#pricelist_select center p').text(order_pricelist.name);
			var all = $('.product');
			self.pos.all_products.forEach(function(product) {
				product.price = self.pos.db.price_dict[order_pricelist.id][product.id][0][0];
				self.pos.chrome.screens.products.product_list_widget.product_cache.clear_node(product.id);
			});
			var lines = self.get_orderlines();
			for (var i = 0; i < lines.length; i++) {
			    var product = lines[i].get_product();
			    if (lines[i].barcode_id){
			        lines[i].set_unit_price(self.pos.db.price_dict[order_pricelist.id][product.id][lines[i].barcode_id]);
			    }
			    else{
			        lines[i].set_unit_price(self.pos.db.price_dict[order_pricelist.id][product.id][0]);
			    }


//			    console.log(product.id);
//			    set_unit_price
//                return lines[i].get_unit_price();

            }
			self.pos.chrome.screens.products.product_list_widget.renderElement()
			self.pos.get_order().save_to_db();
		},
	});
//
	screens.PaymentScreenWidget.include({
		//--To alert the user when the customer is changed and some orderlines already exist in the current order--
		show: function(){
			var current_order = self.pos.get_order();
			this._super();
			if(current_order.need_to_remove_orderlines){
				current_order.need_to_remove_orderlines = false;
				self.pos.gui.show_popup('pos_customer_pricelist_custom_message', {
					'title': _t('Pricelist Change!'),
					'body': _t('This will change the pricelist and you already have some products added with the current pricelist. Please remember to remove and add them again in order to reflect the updated prices.'),
				});
			}
		}
	});

	screens.ProductScreenWidget.include({
		//--To set updated prices of the products whenever ProductScreen appears--
		show: function() {
			var self = this;
			var current_order = self.pos.get_order();
			this._super();
			this.numpad.state.reset();
			if(self.pos.db.price_dict){
				if (current_order.get_client() == null) {
					if ($('div#pricelist_select center p').text() == "") {
						current_order.change_pricelist();
					}
				}
				else{
					var customer_pricelist_id = self.pos.get_client().property_product_pricelist[0];
					if(self.pos.db.pricelist_by_id[customer_pricelist_id]){
						current_order.order_pricelist = self.pos.db.pricelist_by_id[customer_pricelist_id]
						current_order.change_pricelist();
					}
				}
			}
			if(current_order.need_to_remove_orderlines){
				current_order.need_to_remove_orderlines = false;
				self.pos.gui.show_popup('pos_customer_pricelist_custom_message', {
					'title': _t('Pricelist Change!'),
					'body': _t('This will change the pricelist and you already have some products added with the current pricelist. Please remember to remove and add them again in order to reflect the updated prices.'),
				});
			}
		},
	});
});
