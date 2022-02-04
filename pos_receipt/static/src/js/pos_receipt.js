odoo.define("pos_receipt.pos_receipt",function (require) {

    var bus = require('bus.bus').bus;
    var core = require('web.core');
    var framework = require('web.framework');
    var Model = require('web.DataModel');
    var screens = require('point_of_sale.screens');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var models = require('point_of_sale.models');
    var data = require('web.data');
    var chrome = require('point_of_sale.chrome');
    var pop_up = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var QWeb = core.qweb;
    var _t = core._t;

    var pos_booking_model = new Model("pos.booking");
    var hr_employee_model = new Model('hr.employee');
    var SendToKitchenButton = PosBaseWidget.extend({
        template: 'SendToKitchenButton',
    });

    var CustomerReceiptButton = PosBaseWidget.extend({
        template: 'CustomerReceiptButton',
    });

    var KitchenReceiptButton = PosBaseWidget.extend({
        template: 'KitchenReceiptButton',
    });

    var AddSequence = PosBaseWidget.extend({
        template: 'AddSequence',
    })

    models.PosModel.prototype.models.push({
        model:  'pos.category',
        fields: ['id','name','parent_id','child_id','image'],
        domain: null,
        loaded: function(self, categories){
            self.categories = categories;
            var pos_category_model = new Model('pos.category');
            pos_category_model.call("get_root_of_category").done(function(root_category_data){
                self.root_category = root_category_data;
            });
        },
    });

//my code******************************************************************N E W  C O D E****************************************************************************************

////    var models = require('point_of_sale.models');
//    var _super_posmodel = models.PosModel.prototype;
//    models.PosModel = models.PosModel.extend({
//        initialize: function (session, attributes) {
//            var partner_model = _.find(this.models, function(model){ return model.model === 'product.product'; });
//            partner_model.fields.push('arabic_name');
//            return _super_posmodel.initialize.call(this, session, attributes);
//        },
//    });


//*******************************************************************************************************************************************************************************

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        delete_current_order: function(){
            var order = this.get_order();
            var posOrderModel = new Model('pos.order');
            if (order) {
                var self = this;
                if(order.attributes.id){
                    var orderline_status;
                    _.each(order.orderlines.models,function(orderline){
                        if(orderline.order_line_state != 'draft') {
                            self.gui.show_popup('alert',{
                                title:_t('Warning'),
                                warning_icon : true,
                                body: _t('Current order can not be remove'),
                            });
                            orderline_status=true
                        }
                    })
                    if(!orderline_status) {
                        framework.blockUI();
                        posOrderModel.call("close_order", [[order.attributes.id]]).then(function(callback){
                            framework.unblockUI();
                            if(callback){
                                if(order.get_booking_id()){
                                    pos_booking_model.call("write",[order.get_booking_id(),{'state':'cancel'}]);
                                }
                                self.update_emp_state(order);
    //                            if(self.get('orders').last()){
    //                                self.set({ selectedOrder: self.get('orders').last() });
    //                            }
                            }else if(! callback){
                                self.gui.show_popup('alert',{
                                    title:_t('Warning !'),
                                    warning_icon : true,
                                    body: _t('Can not remove order.'),
                                });
                            }
                        },function(err,event) {
                            event.preventDefault();
                            var table_details = order.attributes.table_data;
                            order.offline_delete_order = true;
                            if(table_details != undefined){
                                self.push_order(order);
                                self.update_table_details(table_details);
                            }
                            self.update_emp_state(order);
                        });
                    }
                }else{
                    if(order.get_booking_id()){
                        pos_booking_model.call("write",[order.get_booking_id(),{'state':'cancel'}]);
                    }
                    var self = this;
                    var table_details = order.attributes.table_data;
                    if(table_details != undefined){
                        var restaurant_table_model =  new Model('restaurant.table');
                        if(!order.attributes.split_order){
                            framework.blockUI();
                            restaurant_table_model.call("remove_table_order", [table_details]).then(function(callback){
                                framework.unblockUI();
                                self.update_emp_state(order);
                            },function(err,event) {
                                event.preventDefault();
                                if(!order.attributes.offline_order){
                                    self.db.add_table_order(order);
                                }
                                self.update_emp_state(order);
                            });
                            self.update_table_details(table_details);
                        }else{
                            self.update_emp_state(order);
                        }
                    }
                    self.update_emp_state(order);
                }
            }
        },
        update_table_details : function(data){
            var self = this;
            if(data != undefined && data[0] != undefined && data[0].table_id){
                var table_id = data[0].table_id
                var reserver_seat = parseInt(data[0].reserver_seat)
                for(var i=0;i<self.table_details.length;i++){
                    if (self.table_details[i].id === table_id) {
                        self.table_details[i].available_capacities = self.table_details[i].available_capacities - reserver_seat
                        self.table_details[i].state = 'available'
                        break;
                    }
                }
            }
        },
    });

    chrome.Chrome.include({
        build_widgets: function(){
            this._super();
            this.do_call_recursive();
        },
        offline_orders : function(db_orders,options){
            var self = this;
            push_order_call = true;
            self.pos._flush_offline_order(db_orders, options).done(function (server_ids) {
                var pending = self.pos.db.get_orders().length;
                self.pos.set('synch', {
                    state: pending ? 'connecting' : 'connected',
                    pending: pending
                });
                framework.unblockUI();
            });
        },
        set_transfer_order : function(callback){
            var self = this;
            if(callback){
                _.each(callback,function(ord){
                    var flag = true;
                    for(o in self.pos.attributes.orders.models){
                        if(self.pos.attributes.orders.models[o].attributes.name == ord.pos_reference){
                            flag = false;
                            break;
                        }
                    }
                    if(flag){
                        var selected_order = new models.Order({},{ pos: self.pos });
                        var template = '<span class="order-sequence">' + selected_order.sequence_number + '</span>'
                        $("#"+ selected_order.name.replace(' ', '_')).attr("name", ord.order_name);
                        $("#"+ selected_order.name.replace(' ', '_')).attr("item", ord.order_name);
                        if(ord.reserved_seat){
                            $("#"+ selected_order.name.replace(' ', '_')).attr("data", ord.reserved_seat);
                            selected_order.attributes.table_data = ord.table_data;
                            selected_order.attributes.reserved_seat = ord.reserved_seat;
                            selected_order.set('table_data', ord.table_data);
                            selected_order.set('reserved_seat', ord.reserved_seat);
                        }
                        $("#"+selected_order.name.replace(' ', '_')).html(template + ord.order_name);
                        selected_order.attributes.creationDate = ord.order_name;
                        selected_order.attributes.creationDateId = ord.order_name;
                        selected_order.set('creationDate',ord.order_name);
                        selected_order.set('creationDateId', ord.creation_date_id);
                        if(ord.table_ids){
                            selected_order.attributes.table_ids = ord.table_ids;
                            selected_order.set('table_ids', ord.table_ids);
                        }
                        if(ord.pflag) {
                            selected_order.set('creationDate',false);
                        }
                        if(ord.driver_name){
                            selected_order.set('creationDate',false);
                            selected_order.set('driver_name',ord.driver_name);
                        }
                        if(ord.beautician_id){
                            selected_order.set('beautician_id',ord.beautician_id);
                        }
                        selected_order.set('name',ord.pos_reference);
                        selected_order.attributes.name = ord.pos_reference;
                        selected_order.attributes.id = ord.id;
                        selected_order.attributes.pflag = ord.pflag;
                        selected_order.attributes.parcel = ord.parcel;
                        selected_order.attributes.phone = ord.phone;
                        selected_order.set('pflag',ord.pflag);
                        selected_order.set('parcel',ord.parcel);
                        selected_order.set('phone',ord.phone);
                        if (ord.partner_ids) {
                          var partner = self.pos.db.get_partner_by_id(ord.partner_ids);
                          selected_order.set_client(partner);
                        }
                        if(ord.booking_id){
                            selected_order.set_booking_id(ord.booking_id);
                        }
                         var products = [];
                         _.each(ord.lines, function(get_line){
                             product = self.pos.db.get_product_by_id(get_line.product_id);
                             var line_set = new models.Orderline({}, {pos: self.pos, order: selected_order, product: product});
                             line_set.id = get_line.id;
                             line_set.line_id = get_line.id;
                             line_set.quantity = get_line.qty;
                             line_set.set_quantity(get_line.qty);
                             line_set.price = get_line.price_unit;
                             line_set.set_unit_price(get_line.price_unit);
                             line_set.discount = get_line.discount;
                             line_set.set_discount(get_line.discount);
                             line_set.set_product_lot(product);
                             line_set.set_order_line_state(get_line.order_line_state);
                             line_set.set_order_line_beautician_id(get_line.beautician_id);
                             line_set.set_order_line_beautician(get_line.beautician_name);
                             products.push(product);
                             selected_order.orderlines.add(line_set);
                         });
                         var pos_order_model = new Model('pos.order');
                         pos_order_model.call("write",[[ord.id],{'is_transfer_to_session':false}]).then(function(callback){},function(err,event) {event.preventDefault();});
                         self.pos.get('orders').add(selected_order);
                         selected_order.select_orderline(selected_order.get_last_orderline());
                    }
                });
                if(self.pos.get('orders').size() > 0){
                    self.pos.set({'selectedOrder' : self.pos.get('orders').last()});
                    self.gui.show_screen('products');
                }
            }else{
                self.gui.show_popup('alert',{
                    title:_t('Warning !'),
                    body: _t("There is no any draft orders!!")
                });
            }
        },
        do_call_recursive: function(){
            var self = this;
            var order_ids = [];
            var posOrderModel = new Model('pos.order');
            _.each(this.pos.attributes.orders.models, function(order){
                if(order.attributes.id){
                    order_ids.push(order.attributes.id);
                    clearInterval(self[order.uid]);
                    $("span[data-uid="+order.uid+ "]").closest("span").css({"visibility": "visible"});
                }
            });
            if(order_ids != []){
                posOrderModel.call("get_done_orderline", [order_ids]).then(function(callback){
                    if(callback[1]){
                        self.set_transfer_order(callback[1]);
                    }
                    var unpaid_orders = self.pos.db.get_unpaid_orders();
                    if(unpaid_orders.length != 0){
                        var order_ids_to_sync = _.omit( _.indexBy(unpaid_orders, 'offline_order_name'), 'false','undefined');
                        if(_.size(order_ids_to_sync) != 0){
                            framework.blockUI();
                            var table_vals = {};
                            _.each(order_ids_to_sync,function(order,key){
                                if(order.table_data && order.table_data.length > 0){
                                    if(!order.split_order){
                                    _.each( order.table_data,function(table_record){
                                            if(_.has(table_vals,table_record.table_id)){
                                                table_vals[table_record.table_id] = parseInt(table_vals[table_record.table_id]) + parseInt(table_record.reserver_seat);
                                            }else{
                                                table_vals[table_record.table_id] = parseInt(table_record.reserver_seat);
                                            }
                                        });
                                    }
                                }
                            });
                            var restaurant_table_model =  new Model('restaurant.table');
                            restaurant_table_model.call("update_offline_table_order", [table_vals]).done(function(){
                                framework.unblockUI();
                                var table_vals = {};
                                _.each(order_ids_to_sync,function(order,key){
                                    if(order.table_data && order.table_data.length > 0){
                                        _.each( order.table_data,function(table_record){
                                            if(_.has(table_vals,table_record.table_id)){
                                                table_vals[table_record.table_id] = parseInt(table_vals[table_record.table_id]) + parseInt(table_record.reserver_seat);
                                            }else{
                                                table_vals[table_record.table_id] = parseInt(table_record.reserver_seat);
                                            }
                                        });
                                        order.offline_order_name = false;
                                        self.pos.db.save_unpaid_update_order(order);
                                    }
                                });
                                _.each(table_vals,function(val,table_id){
                                    var table_res = {'available_capacities': val};
                                    for(var i=0;i < self.pos.table_details.length;i++){
                                        if (self.pos.table_details[i].id === parseInt(table_id)) {
                                            var final_capacity = parseInt(self.pos.table_details[i].available_capacities) + parseInt(table_res.available_capacities);
                                            self.pos.table_details[i].available_capacities = final_capacity;
                                            if(parseInt(self.pos.table_details[i].capacities) -final_capacity === 0){
                                                self.pos.table_details[i].state = 'reserved';
                                            }
                                            break;
                                        }
                                    }
                                });
                                if(self.gui.get_current_screen() == 'floors'){
                                    self.gui.screen_instances.floors.renderElement();
                                }
                            })
                        }else{
                            if(self.gui.get_current_screen() == 'floors'){
                                self.gui.screen_instances.floors.renderElement();
                            }
                        }
                    }else{
                        if(self.gui.get_current_screen() == 'floors'){
                            self.gui.screen_instances.floors.renderElement();
                        }
                    }
                    
                    var db_table_orders = self.pos.db.get_table_orders();
                    var db_orders = self.pos.db.get_orders();
                    if(db_table_orders.length != 0 && db_orders.length != 0){
                        framework.blockUI();
                        var restaurant_table_model =  new Model('restaurant.table');
                        restaurant_table_model.call("remove_delete_table_order", [db_table_orders]).then(function(callback1){
                            self.pos.db.remove_all_table_orders();
                            self.offline_orders(db_orders,options);
                        }).fail(function (error, event){
                            event.preventDefault();
                            self.offline_orders(db_orders,options);
                        });
                    }else if(db_table_orders.length != 0) {
                        framework.blockUI();
                        var restaurant_table_model =  new Model('restaurant.table');
                        restaurant_table_model.call("remove_delete_table_order", [db_table_orders]).then(function(callback1){
                            framework.unblockUI();
                            self.pos.db.remove_all_table_orders();
                        }).fail(function (error, event){
                            framework.unblockUI();
                            event.preventDefault();
                        });
                    }else if(db_orders.length != 0) {
                        if(self.gui.get_current_screen() != 'payment' && self.gui.get_current_screen() != 'receipt'){
                            framework.blockUI();
                            self.offline_orders(db_orders,options);
                        }
                    }else{
                        //framework.unblockUI();
                    }
                    _.each(self.pos.attributes.orders.models, function(order){
                        if(callback[0]){
                            _.each(callback[0], function(ord){
                                if(ord.id == order.attributes.id){
                                    var set = false;
                                    self[order.uid] = setInterval(function() {
                                        $("span[data-uid="+order.uid+ "]").closest("span").css({
                                            "visibility": set ? "hidden" : "visible",
                                        });
                                        set = !set;
                                    }, 800); 
                                }
                            });
                        }
                    });
                },function(err,event) {
                    event.preventDefault();
                });
                setTimeout(function() { self.do_call_recursive() },10000)
            }else{
                setTimeout(function() { self.do_call_recursive() },10000)
            }
        },
    });

    var SquencePopupWidget = pop_up.extend({
        template:'SquencePopupWidget',
        show: function(options){
            options = options || {};
            var self = this;
            this._super();
            this.options = options;
            this.title = options.title;
            this.category_data = options.category_data
            this.send_to_kitchen = options.send_to_kitchen || false;
            this.orderlines = [];
            this.orderlines = self.pos.get('selectedOrder').orderlines.models;
            this.renderElement();
            self.hotkey_handler = function(event){
                if(event.which === 27){
                    self.gui.close_popup();
                }
            };
            $('body').on('keyup',self.hotkey_handler);
        },
        click_confirm: function(){
            this.gui.close_popup();
            if( this.options.confirm ){
                this.options.confirm.call(this);
            }
        },
        close:function(){
            this._super();
            $('body').off('keyup',this.hotkey_handler);
        },
    });
    gui.define_popup({name:'sequence_popup', widget: SquencePopupWidget});

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
            var self =this
            self.set({
                'id': null,
            })
            _super_order.initialize.apply(this,arguments);
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            var self = this;
            self.attributes.id = json.id;
        },
        add_product: function(product, options){
            this._printed = false;
            _super_order.add_product.apply(this,arguments);
        },
        export_as_JSON : function(json) {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            var self = this;
            json.id =  self.attributes.id;
            json.creation_date =  self.validation_date || self.creation_date;
            return json;
        },
    });

    var _super_order_line = models.Orderline.prototype;
    var temporary_sequence_number = 1;
    models.Orderline = models.Orderline.extend({
        initialize: function() {
            this.temporary_sequence_number = temporary_sequence_number++;
            this.sequence_number = 1;
            this.beautician_id = false;
            _super_order_line.initialize.apply(this,arguments);
        },
        init_from_JSON: function(json) {
            _super_order_line.init_from_JSON.apply(this,arguments);
            var self = this;
            self.line_id = json.line_id;
            self.order_line_state_id = json.order_line_state_id;
            self.beautician_id = json.beautician_id;
        },
        set_line_id : function(line_id){
            this.line_id = line_id;
            this.trigger('change',this);
        },
        set_beautician_id : function(beautician_id){
            this.beautician_id = beautician_id;
        },
        get_beautician_id : function(){
            return this.beautician_id;
        },
        export_as_JSON : function(json) {
            var json = _super_order_line.export_as_JSON.apply(this,arguments);
            var self = this;
            json.line_id =  self.line_id;
            json.order_line_state_id = 1;
            json.beautician_id = self.get_beautician_id();
            return json;
        },
    });

    var ActionpadWidget = PosBaseWidget.extend({
        template: 'ActionpadWidget',
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
            this.pos.bind('change:selectedClient', function() {
                self.renderElement();
            });
        },
        renderElement: function() {
            var self = this;
            $('.pay').unbind('click').bind('click',function(){
                var done_counter = 0;
                var progress_counter = 0;
                var last_progress_orderline_state_change = false;
                _.each(self.pos.attributes.selectedOrder.orderlines.models,function(line){
                    if(line.get_order_line_state() == "done"){
                        done_counter = done_counter + 1;
                    }
                });
                if(done_counter != self.pos.attributes.selectedOrder.orderlines.models.length){
                    self.gui.show_popup('alert',{
                        title:_t('Warning !'),
                        body: _t('Please done all order line.'),
                    });
                    return false;
                }
                var currentOrder = self.pos.get('selectedOrder');
                if(!currentOrder.attributes.client){
                    self.gui.show_popup('alert',{
                        title:_t('Warning !'),
                        body: _t('Please Select Customer.'),
                    });
                    return false;
                }
                currentOrder.kitchen_receipt = false;
                currentOrder.customer_receipt = false;
                self.gui.show_screen('payment');
            });
            this._super();
        }
    });

    screens.ProductScreenWidget.include({
        start: function(){
            var self = this;
            this._super();
            this.actionpad = new ActionpadWidget(this,{});
            this.actionpad.replace(this.$('.placeholder-ActionpadWidget'));
            
            this.SendToKitchenButton = new SendToKitchenButton(this,{});
            this.SendToKitchenButton.appendTo(this.$('.placeholder-OptionsListWidget .option_list_box_container'));
            
            this.CustomerReceiptButton = new CustomerReceiptButton(this,{});
            this.CustomerReceiptButton.appendTo(this.$('.placeholder-OptionsListWidget .option_list_box_container'));
            
            this.KitchenReceiptButton = new KitchenReceiptButton(this,{});
            this.KitchenReceiptButton.appendTo(this.$('.placeholder-OptionsListWidget .option_list_box_container'));
            
            this.AddSequence = new AddSequence(this,{});
            this.AddSequence.appendTo(this.$('.placeholder-OptionsListWidget .option_list_box_container'));

            this.$(".send_to_kitchen_button").on('click',function(){
                self.send_to_kitchen();
            });
            
            this.$(".customer_receipt_button").on('click',function(){
                self.customer_receipt();
            });
            
            this.$(".kitchen_receipt_button").on('click',function(){
                self.kitchen_receipt();
            });
            
            this.$(".add_sequence").on('click',function(){
                self.add_sequence();
            });
        },
        send_to_kitchen : function(){
            var self = this;
            if(self.pos.attributes.selectedOrder.orderlines.models == ''){
                self.gui.show_popup('alert',{
                     title:_t('Warning !'),
                     body: _t('Can not create order which have no order line.'),
                });
                return false;
            }else{
                var order = [];
                var current_order = this.pos.get_order();
                var posOrderModel = new Model('pos.order');
                order.push({'data':current_order.export_as_JSON()})
                posOrderModel.call('create_from_ui',[order, true]).then(function(callback){
                   current_order.attributes.id = callback[0];
                   for( idx in current_order.orderlines.models){
                       current_order.orderlines.models[idx].line_id = callback[1][idx];
                       current_order.orderlines.models[idx].set_line_id(callback[1][idx]);
                   }
                },function(err,event) {
                    event.preventDefault();
                });
                setTimeout(function(){
                    self.gui.show_popup('alert',{
                        title:_t('Successful'),
                        warning_icon : false,
                        body: _t('Order send to the kitchen successfully!'),
                   });
                },300);
            }
        },
        kitchen_receipt : function(){
            var self = this;
            var currentOrder = self.pos.get('selectedOrder');
            if(self.pos.attributes.selectedOrder.orderlines.models == ''){
                self.gui.show_popup('alert',{
                    title:_t('Warning !'),
                    body: _t('Can not Print order which have no order line.'),
               });
               return false;
            }else{
                var currentOrder = self.pos.get('selectedOrder');
               // self.create_from_ui(currentOrder.export_as_JSON(),true,false);
                currentOrder.kitchen_receipt = true;
                currentOrder.customer_receipt = false;
                _.each(currentOrder.orderlines.models, function(order_line){
                    order_line.categ_name = "All";
                    order_line.product_name = order_line.product.display_name;
                    order_line.print_qty = order_line.quantity;
                    order_line.print = true;
                    order_line.ol_flag = false;
                });
                if(self.pos.config.iface_print_via_proxy){
                    var receipt = currentOrder.export_for_printing();
                    self.pos.proxy.print_receipt(QWeb.render('kitchen_receipt',{
                        receipt: receipt,
                        widget: self,
                        order:currentOrder,
                        orderlines: currentOrder.orderlines.models,
                    }));
                }else{
                    self.gui.show_screen('receipt');
                }
            }
        },
        customer_receipt : function(){
            var self = this;
            if(self.pos.attributes.selectedOrder.orderlines.models == ''){
                self.gui.show_popup('alert',{
                    title:_t('Warning !'),
                    warning_icon : true,
                    body: _t('Can not Print order which have no order line.'),
                });
                return false;
            }else{
                
                var currentOrder = self.pos.get('selectedOrder');
                currentOrder.kitchen_receipt = false;
                currentOrder.customer_receipt = true;
                if(self.pos.config.iface_print_via_proxy){
                    var receipt = currentOrder.export_for_printing();
                    self.pos.proxy.print_receipt(QWeb.render('XmlReceipt',{
                        widget: self,
                        pos:self.pos,
                        receipt: receipt,
                        order:currentOrder,
                        orderlines: currentOrder.orderlines.models,
                        paymentlines: currentOrder.get_paymentlines(),
                    }));
                }else{
                   self.gui.show_screen('receipt');
                }
            }
        },
        category_data : function(){
            var self = this;
            var currentOrder = self.pos.get('selectedOrder');
            var duplicate_root_category_id = [];
            var res = [];
            _.each(self.pos.get('selectedOrder').orderlines.models,function(line){
                var root_category_id;
                var root_category_name;
                if(self.pos.root_category[line.product.pos_categ_id[0]] == undefined){
                    root_category_id = 'Undefined';
                    root_category_name = 'Undefined'
                }else if( ! self.pos.root_category[line.product.pos_categ_id[0]].root_category_name){
                    root_category_id = self.pos.root_category[line.product.pos_categ_id[0]].categ_id;
                    root_category_name = self.pos.root_category[line.product.pos_categ_id[0]].categ_name;
                }else{
                    root_category_id = self.pos.root_category[line.product.pos_categ_id[0]].root_category_id;
                    root_category_name = self.pos.root_category[line.product.pos_categ_id[0]].root_category_name;
                }
                if(duplicate_root_category_id.indexOf(root_category_id) == -1){
                    duplicate_root_category_id.push(root_category_id);
                    res.push({'id':root_category_id,'name':root_category_name,'data':[{'product':line.product,'qty':line.quantity,'sequence_number':line.sequence_number,'temporary_sequence_number':line.temporary_sequence_number}]})
                }else{
                    _.each(res,function(record){
                        if(record['id'] == root_category_id){
                            product_categ_data = [];
                            product_categ_data = record['data'];
                            product_categ_data.push({'product':line.product,'qty':line.quantity,'sequence_number':line.sequence_number,'temporary_sequence_number':line.temporary_sequence_number});
                            record['data'] = product_categ_data;
                        }
                    });
                }
            });
            return res;
        },
        add_sequence : function(){
            var self = this;
            if(self.pos.attributes.selectedOrder.orderlines.models == ''){
                self.gui.show_popup('alert',{
                    title:_t('Warning !'),
                    warning_icon : true,
                    body: _t('Can not create order which have no order line.'),
                });
                return false;
            }else{
                self.gui.show_popup('sequence_popup',{
                    title:_t('Orderline Sequence'),
                    send_to_kitchen :true,
                    category_data:self.category_data(),
                    'confirm': function(value) {
                        var dict = {}
                        $('#sequence_data tr input').each(function(index){
                             var temporary_sequence_number_value = $(this).attr('temporary_sequence_number');
                             dict[temporary_sequence_number_value] = $("#sequence_data tr input[temporary_sequence_number="+ temporary_sequence_number_value +"]").val()
                        })
                        _.each(self.pos.get('selectedOrder').orderlines.models,function(line){
                            line.sequence_number = parseInt(dict[line.temporary_sequence_number])
                        });
                        self.pos.get('selectedOrder').orderlines.models.sort(function(a, b){
                            return a['sequence_number'] - b['sequence_number'];
                        });
                    },
                });
            }
        },
    });

    screens.NumpadWidget.include({
        clickSwitchSign: function() {
            var self = this;
            var order = this.pos.get('selectedOrder');
            if(order.selected_orderline && order.selected_orderline.get_order_line_state() != 'draft'){
                self.gui.show_popup('alert',{
                    title:_t('Warning'),
                    warning_icon : true,
                    body: _t("Done orderline can't change"),
                });
                return false;
            }else{
                return this.state.switchSign();
            }
        },
        clickAppendNewChar: function(event) {
            var self = this;
            var order = this.pos.get('selectedOrder');
            if(order.selected_orderline && order.selected_orderline.get_order_line_state() != 'draft'){
                self.gui.show_popup('alert',{
                    title:_t('Warning'),
                    warning_icon : true,
                    body: _t("Done orderline can't change"),
                });
                return false;
            }else{
                var newChar;
                newChar = event.currentTarget.innerText || event.currentTarget.textContent;
                return this.state.appendNewChar(newChar);
            }
        },
        clickChangeMode: function(event) {
            var self = this;
            var order = this.pos.get('selectedOrder');
            if(order.selected_orderline && order.selected_orderline.get_order_line_state() != 'draft'){
                self.gui.show_popup('alert',{
                    title:_t('Warning'),
                    warning_icon : true,
                    body: _t("Done orderline can't change"),
                });
                return false;
            }else{
                var newMode = event.currentTarget.attributes['data-mode'].nodeValue;
                return this.state.changeMode(newMode);
            }
        },
        update_emp_state : function(selected_orderline){
            var self = this;
            var beautician_id = [];
            if(selected_orderline && selected_orderline.get_order_line_beautician_id()){
                beautician_id.push(parseInt(selected_orderline.get_order_line_beautician_id()))
            }
            framework.blockUI();
            if(beautician_id.length > 0){
                hr_employee_model.call("write",[beautician_id,{'state':'available'}]).done(function(){
                    selected_orderline.set_order_line_beautician_id(false);
                    selected_orderline.set_order_line_beautician("");
                    framework.unblockUI();
                    return self.state.deleteLastChar();
                });
            }else{
                framework.unblockUI();
                return self.state.deleteLastChar();
            }
        },
        clickDeleteLastChar: function() {
            var self = this;
            var order = this.pos.get('selectedOrder');
            if(order.selected_orderline != undefined){
                if(order.selected_orderline.line_id && this.state.get('mode') != 'price' && this.state.get('mode') != 'discount'){
                     (new Model('pos.order.line')).get_func('orderline_state_id')(order.selected_orderline.line_id,order.attributes.id).then(function(state_id){
                         if(state_id == 1){
                             if(order.selected_orderline.get_order_line_state() != 'draft'){
                                 self.gui.show_popup('alert',{
                                     title:_t('Warning'),
                                     warning_icon : true,
                                     body: _t('Current orderline is not remove'),
                                 });
                                 return false;
                             }else{
                                 self.pos_orderline_dataset = new data.DataSetSearch(self, 'pos.order.line', {}, []);
                                 self.pos_orderline_dataset.unlink([order.selected_orderline.line_id]);
                                 return self.update_emp_state(order.selected_orderline);
                                 //return self.state.deleteLastChar();
                             }
                         }else if(state_id == 'cancel'){
                             if(order.selected_orderline.get_order_line_state() != 'draft'){
                                 self.gui.show_popup('alert',{
                                     title:_t('Warning'),
                                     warning_icon : true,
                                     body: _t('Current orderline is not remove'),
                                 });
                                 return false;
                             }else{
                                 return self.update_emp_state(order.selected_orderline);
                                // return self.state.deleteLastChar();
                             }
                         }else if(state_id != 1){
                             self.gui.show_popup('alert',{
                                 title:_t('Warning'),
                                 warning_icon : true,
                                 body: _t('Current orderline is not remove'),
                             });
                             return false;
                         }
                     });
                 }
                else{
                     return self.update_emp_state(order.selected_orderline);
                    // return self.state.deleteLastChar();
                 }
                if(order.booking_id){
                    if(order.selected_orderline.product.id && order.selected_orderline.quantity == 0){
                       var pos_booking_orderline = new data.DataSet(this,'pos.booking',{},[]);
                       pos_booking_orderline.call('state_change_booking_orderline',[[order.selected_orderline.id],{'product_id':order.selected_orderline.product.id,'booking_id':order.selected_orderline.order.booking_id}]).done(function(result){
                       })
                    }
                }
             }
            else{
                 return self.state.deleteLastChar();
             }
        },
    });

    screens.ReceiptScreenWidget.include({
        click_back: function() {
            this.gui.show_screen('products');
        },
        show: function(){
            this._super();
            var self = this;
            var order = this.pos.get_order()
            var is_spa_order = order.spa_order_receipt;
            var is_confirm_receipt = order.confirm_receipt;
            var is_kitchen = order.kitchen_receipt;
            if(!is_kitchen){
                if(! order.customer_receipt){
                    this.$('.next').show();
                    this.$('.back').hide();
                    this.$('.change-value').parent().show();
                }else{
                    this.$('.next').hide();
                    this.$('.change-value').parent().hide();
                    this.$('.back').show();
                    if(is_spa_order){
                        this.$('.next').show();
                        this.$('.change-value').parent().show();
                        this.$('.back').hide();
                        self.pos.db.remove_unpaid_order(order);
                    }
                }
            }else{
                this.$('.next').hide();
                this.$('.change-value').parent().hide();
            }
            /*Set barcode in pos ticket.*/
            var barcode_val = order.get_name();
            if(order.get_pos_reference()){
                barcode_val = order.get_pos_reference();
            }
            if (barcode_val) {
               $("#barcode_div").addClass(barcode_val.toString());
               $("#barcode_div").barcode(barcode_val.toString(), "code128");
            }
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.back').click(function(){
                self.click_back();
            });
        },
    });

    var splitBillScreenWidget;
    var pos_config_dataset = new data.DataSet(this,'pos.config',{},[]);
    pos_config_dataset.call('check_is_pos_restaurant').done(function(result){
        if(result){
            if(result){
                _.each(gui.Gui.prototype.screen_classes,function(screen_class){
                    if(screen_class.name == "splitbill"){
                        splitBillScreenWidget = screen_class;
                    }
                });
                splitBillScreenWidget.widget.include({
                    renderElement: function(){
                        var order = this.pos.get_order();
                        if(!order){
                            return;
                        }
                        order.kitchen_receipt = false;
                        order.customer_receipt = false;
                        this._super();
                    },
                    pay: function(order,neworder,splitlines){
                        var orderlines = order.get_orderlines();
                        var empty = true;
                        var full  = true;
                        var self = this;
                        for(var i = 0; i < orderlines.length; i++){
                            var id = orderlines[i].id;
                            var split = splitlines[id];
                            if(!split){
                                full = false;
                            }else{
                                if(split.quantity){
                                    empty = false;
                                    if(split.quantity !== orderlines[i].get_quantity()){
                                        full = false;
                                    }
                                }
                            }
                        }
                        if(empty){
                            return;
                        }
                        if(full){
                            neworder.destroy({'reason':'abandon'});
                            this.gui.show_screen('payment');
                        }else{
                            for(var id in splitlines){
                                var split = splitlines[id];
                                var line  = order.get_orderline(parseInt(id));
                                line.set_quantity(line.get_quantity() - split.quantity);
                                if(Math.abs(line.get_quantity()) < 0.00001){
                                    order.remove_orderline(line);
                                }
                                if(line.line_id != undefined){
                                    var data = require('web.data');
                                    self.pos_line = new data.DataSetSearch(self, 'pos.order.line');
                                    self.pos_line.unlink(line.line_id)
                                }
                                delete splitlines[id];
                            }
                            neworder.set_screen_data('screen','payment');
                            // for the kitchen printer we assume that everything
                            // has already been sent to the kitchen before splitting 
                            // the bill. So we save all changes both for the old 
                            // order and for the new one. This is not entirely correct 
                            // but avoids flooding the kitchen with unnecessary orders. 
                            // Not sure what to do in this case.
                            if ( neworder.saveChanges ) { 
                                order.saveChanges();
                                neworder.saveChanges();
                            }
                            neworder.set_customer_count(1);
                            order.set_customer_count(order.get_customer_count() - 1);
                            $.ajax({
                                type: 'GET',
                                success: function() {
                                    neworder.set('offline_order',false);
                                    neworder.set('offline_order_name',false)
                                    self.pos.db.save_unpaid_order(neworder);
                                },
                                error: function(XMLHttpRequest, textStatus, errorThrown) {
                                    neworder.set('offline_order',true);
                                    neworder.set('offline_order_name',neworder.name)
                                    self.pos.db.save_unpaid_order(neworder);
                                }
                            });
                          // self.pos.db.save_unpaid_order(neworder);
                            this.pos.get('orders').add(neworder);
                            this.pos.set('selectedOrder',neworder);
                            this.gui.show_screen('payment');
                        }
                    },
                    show : function(){
                        var self = this;
                        screens.ScreenWidget.prototype.show.call(this)
                        this.renderElement();
                        var order = this.pos.get_order();
                        var neworder = new models.Order({},{
                            pos: this.pos,
                            temporary: true,
                        });
                        neworder.set('client',order.get('client'));
                        neworder.set('pflag',order.get('pflag'));
                        neworder.set('parcel',order.get('parcel'));
                        neworder.set('pricelist_id',order.get('pricelist_id'));
                        neworder.set('phone',order.get('phone'));
                        neworder.set('partner_id',order.get('partner_id'));
                        neworder.set('driver_name',order.get('driver_name'));
                        neworder.set('beautician_id',order.get('beautician_id'));
                        neworder.set('beautician_name',order.get('beautician_name'));
                        neworder.set('creationDate',order.get('creationDate'));
                        neworder.set('table_data',order.get('table_data'));
                        neworder.set('table',order.get('table'));
                        neworder.set('table_ids',order.get('table_ids'));
                        neworder.set('split_order',true);
                     //   neworder.trigger('change',neworder)
                        
                        var splitlines = {};
                        this.$('.orderlines').on('click','.orderline',function(){
                            var id = parseInt($(this).data('id'));
                            var $el = $(this);
                            self.lineselect($el,order,neworder,splitlines,id);
                        });
                        this.$('.paymentmethods .button').click(function(){
                            self.pay(order,neworder,splitlines);
                        });
                        this.$('.back').unbind('click').bind('click',function(){
                            neworder.destroy({'reason':'abandon'});
                            self.gui.show_screen(self.previous_screen);
                        });
                    },
                });
            }
        }
    });

    chrome.Chrome.include({
        build_widgets: function() {
            this._super();
            var self = this;
            bus.on("notification", self, self.on_notification);
            var channel = JSON.stringify([openerp.session.db, 'pos.order', openerp.session.uid]);
            bus.add_channel(channel);
            bus.start_polling();
        },
        on_notification : function(notification){
            var self = this;
            var order_id = false
            var channel = notification[0] ? notification[0][0] ?  notification[0][0] : false : false;
            var message = notification[0] ? notification[0][1] ? notification[0][1] : false : false;
            if((Array.isArray(channel) && (channel[1] === 'pos.order'))){
                if(message){
                    order_id = message['order_id'];
                }
            }
            var all_orders =  self.pos.get('orders').models;
            for(var i=0; i< all_orders.length;i++){
                if(parseInt(order_id ) == parseInt(all_orders[i].get('id'))){
                    all_orders[i].destroy();
                }
            }
        }
    });

});
