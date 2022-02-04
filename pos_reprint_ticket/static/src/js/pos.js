odoo.define('pos_reprint_ticket.pos',function(require){
	"use strict"
	var Model = require('web.DataModel');
	var screens = require('point_of_sale.screens');
	var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var utils = require('web.utils');
	var core = require('web.core');
	var QWeb = core.qweb;
	var _t = core._t;
	var SuperPosModel = models.PosModel.prototype;


	models.load_models([{
			model: 'pos.order',
			fields: ['id', 'name', 'date_order', 'partner_id', 'lines', 'pos_reference','invoice_id'],
			domain: function(self) {
				var domain_list = [];
				domain_list = [['session_id', '=', self.pos_session.name], ['state', 'not in', ['draft', 'cancel']]]
				return domain_list;
			},
			loaded: function(self, wk_order) {
				self.db.pos_all_orders = wk_order;
				self.db.order_by_id = {};
				wk_order.forEach(function(order){
					var order_date = new Date(order['date_order']);
          			var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
					order['date_order'] = new Date(utc).toLocaleString();
					self.db.order_by_id[order.id] = order;
				});
			},
		}, {
			model: 'pos.order.line',
			fields: ['product_id', 'order_id', 'qty','discount','price_unit','price_tax','price_subtotal_incl','price_subtotal'],
			domain: function(self) {
				var order_lines = []
				var orders = self.db.pos_all_orders;
				for (var i = 0; i < orders.length; i++) {
					order_lines = order_lines.concat(orders[i]['lines']);
				}
				return [
					['id', 'in', order_lines]
				];
			},
			loaded: function(self, wk_order_lines) {
				self.db.pos_all_order_lines = wk_order_lines;
				self.db.line_by_id = {};
				wk_order_lines.forEach(function(line){
					self.db.line_by_id[line.id] = line;
				});
			},
		}, ], {
		'after': 'product.product'
	});

models.PosModel = models.PosModel.extend({
		push_and_invoice_order: function(order){
			var self = this;
			var invoiced = new $.Deferred();
			if(!order.get_client()){
				invoiced.reject({code:400, message:'Missing Customer', data:{}});
				return invoiced;
			}
			var order_id = this.db.add_order(order.export_as_JSON());
			this.flush_mutex.exec(function(){
				var done = new $.Deferred();
				var transfer = self._flush_orders([self.db.get_order(order_id)], {timeout:30000, to_invoice:true});
				transfer.fail(function(error){
					invoiced.reject(error);
					done.reject();
				});
				transfer.pipe(function(order_server_id){
					self.chrome.do_action('point_of_sale.pos_invoice_report',{additional_context:{
						//Code chenged for POS All Orders List --START--
						active_ids:[order_server_id.orders[0].id],
						// Code chenged for POS All Orders List --END--
					}});
					invoiced.resolve();
					done.resolve();
				});
				return done;
			});
			return invoiced;
		},

		_save_to_server: function (orders, options) {
			var self = this;
			return SuperPosModel._save_to_server.call(this,orders,options).then(function(return_dict){
				if(return_dict.orders != null){
					return_dict.orders.forEach(function(order){
						if(order.existing)
						{
							self.db.pos_all_orders.forEach(function(order_from_list){
								if(order_from_list.id == order.original_order_id)
									order_from_list.return_status = order.return_status
							});
						}
						else{
							var order_date = new Date(order['date_order'])
							var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
							order['date_order'] = new Date(utc).toLocaleString()
							self.db.pos_all_orders.unshift(order);
							self.db.order_by_id[order.id] = order;
						}
					});
					return_dict.orderlines.forEach(function(orderline){
						if(orderline.existing){
							var target_line = self.db.line_by_id[orderline.id];
							target_line.line_qty_returned = orderline.line_qty_returned;
						}
						else{
							self.db.pos_all_order_lines.unshift(orderline);
							self.db.line_by_id[orderline.id] = orderline;
						}
					});
					if(self.db.all_statements)
						return_dict.statements.forEach(function(statement) {
							self.db.all_statements.unshift(statement);
							self.db.statement_by_id[statement.id] = statement;
					});

				}
				return return_dict;
				//Code for POS All Orders List --start--
			});
		}
	});

var OrdersScreenWidget = screens.ScreenWidget.extend({
		template: 'OrdersScreenWidget',

		init: function(parent, options) {
			this._super(parent, options);
		},
		get_customer: function(customer_id){
			var self = this;
			if(self.gui)
				return self.gui.get_current_screen_param('customer_id');
			else
				return undefined;
		},
		render_list: function(order, input_txt) {
			var self = this;
			var customer_id = this.get_customer();
			var new_order_data = [];
			if(customer_id != undefined){
				for(var i=0; i<order.length; i++){
					if(order[i].partner_id[0] == customer_id)
						new_order_data = new_order_data.concat(order[i]);
				}
				order = new_order_data;
			}
			if (input_txt != undefined && input_txt != '') {
				var new_order_data = [];
				var search_text = input_txt.toLowerCase()
				for (var i = 0; i < order.length; i++) {
					if (order[i].partner_id == '') {
						order[i].partner_id = [0, '-'];
					}
					if (((order[i].name.toLowerCase()).indexOf(search_text) != -1) || ((order[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
						new_order_data = new_order_data.concat(order[i]);
					}
				}
				order = new_order_data;
			}
			var contents = this.$el[0].querySelector('.wk-order-list-contents');
			contents.innerHTML = "";
			var wk_orders = order;
			for (var i = 0, len = Math.min(wk_orders.length, 1000); i < len; i++) {
				var wk_order = wk_orders[i];
				var orderline_html = QWeb.render('WkOrderLine', {
					widget: this,
					order: wk_orders[i],
					customer_id:wk_orders[i].partner_id[0],
				});
				var orderline = document.createElement('tbody');
				orderline.innerHTML = orderline_html;
				orderline = orderline.childNodes[1];
				contents.appendChild(orderline);
			}
		},
		show: function() {
			var self = this;
			this._super();
			var orders = self.pos.db.pos_all_orders;

			for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
            if (orders[i]) {
                var order = orders[i];
                // self.order_string += i + ':' + order.pos_reference + '\n';
            	}
        	}
			this.render_list(orders, undefined);
			this.$('.searchbox input').keyup(function() {
				self.render_list(orders, this.value);
			});
			this.$('.back').on('click',function() {
				console.log('fgf');
				self.gui.show_screen('products');
			});
			this.$('.wk-order-list-contents').delegate('.print-button', 'click', function(event){

                var order_id = $(this).data('id');
                var lines = [];
            	var payments = [];
            	var discount = 0;
            	var subtotal = 0;
            	var order_new = null;
            	var receipt ={};
            	var tax =[];
            	for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
                	if (orders[i] && orders[i].id == order_id) {
                    	order_new = orders[i];
                	}
            	}
                console.log(self.pos.db.pos_all_order_lines);
                if(order_id){
                    (new Model('pos.order')).call('get_orderlines', [order_id])
                    .then(function(result) {

                    	lines = result[0];
                		payments = result[2];
                		discount = result[1];
                		order = result[4];
                		tax = result[5];
                		subtotal=result[6];
                		var cashier = self.pos.cashier || self.pos.user;
                        var company = self.pos.company;
                		receipt['header'] = self.pos.config.receipt_header || '';
                        receipt['footer'] = self.pos.config.receipt_footer || '';
                        receipt['curr_user'] = cashier ? cashier.name : null
                        receipt['shop'] = self.pos.shop;
                        receipt['company'] = {
                            email: company.email,
                            website: company.website,
                            company_registry: company.company_registry,
                            contact_address: company.partner_id[1],
                            vat: company.vat,
                            name: company.name,
                            phone: company.phone,
                            logo: self.pos.company_logo_base64,
                        };
               
                        
                        $('.pos-receipt-container').html(QWeb.render('PosTicket3', {
                            widget:self,
                    		order: order,
                    		change: result[3],
                    		receipt:receipt,
                    		orderlines: lines,
                    		discount_total: discount,
                    		paymentlines: payments,
                    		taxlines:tax,
                    		pos:self.pos,
                    		subtotal:subtotal
                        }));
                        self.gui.show_screen("reprint_ticket");
                        
                    });
                }

                
            });
		},
		close: function() {
			this._super();
			this.$('.wk-order-list-contents').undelegate();
		},
	});
	gui.define_screen({name: 'wk_order',widget:OrdersScreenWidget});

//screens.ProductScreenWidget.include({
//		show: function(){
//			var self = this;
//			this._super();
//			this.product_categories_widget.reset_category();
//			this.numpad.state.reset();
//			$('#all_orders').on('click',function(){
//				self.gui.show_screen('wk_order',{});
//			});
//		},
//	});
var ReprintTicketScreenWidget = screens.ScreenWidget.extend({
        template: 'ReprintTicketScreenWidget',
        show: function() {
            var self = this;
            self._super();
            $('.button.back.wk_reprint_back').on("click", function() {
                self.gui.show_screen('wk_order');
            });
            $('.button.next.wk_reprint_home').on("click", function() {
                self.gui.show_screen('products');
            });
            $('.button.print').click(function() {
                var test = self.chrome.screens.receipt;
                setTimeout(function() {
                    self.chrome.screens.receipt.lock_screen(false);
                }, 1000);
                if (!test['_locked']) {
                    self.chrome.screens.receipt.print_web();
                    self.chrome.screens.receipt.lock_screen(true);
                }
            });
        }
    });
    gui.define_screen({ name: 'reprint_ticket', widget: ReprintTicketScreenWidget });

var TicketReprintButton = screens.ActionButtonWidget.extend({
    template: 'TicketReprintButton',
   	show: function(){
        this._super();
        var self = this;
        this.product_categories_widget.reset_category();
		this.numpad.state.reset();
        // this.$('.ticket_reprint').click(function(){
        //     console.log('hiiiiiiiii');
        // });
    },
    button_click: function(){
    	var self = this;
        this._super();
    	 self.gui.show_screen('wk_order',{});
    },
});

screens.define_action_button({
    'name': 'ticket_receiptbutton',
    'widget': TicketReprintButton,
});

return {
    OrdersScreenWidget: OrdersScreenWidget,
    ReprintTicketScreenWidget:ReprintTicketScreenWidget,
};


});