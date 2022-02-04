odoo.define('pos_salesperson.saleperson',function(require){
	"use strict"
	var Model = require('web.DataModel');
	var screens = require('point_of_sale.screens');
	var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var utils = require('web.utils');
	var core = require('web.core');
	var QWeb = core.qweb;
    var _t = core._t;
	var globalCashier = null;

//var SalesPersonButton = screens.ActionButtonWidget.extend({
//    template: 'SalesPersonButton',
//   	show: function(){
//        this._super();
//        var self = this;
//        this.product_categories_widget.reset_category();
//		this.numpad.state.reset();
//	},
//
//    button_click: function(){
//    	var self = this;
//        this._super();
////    	 self.gui.show_screen('wk_order',{});
//    },
//});
//
//screens.define_action_button({
//    'name': 'saleperson_button',
//    'widget': SalesPersonButton,
//});
//

var _modelproto = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({

        initialize: function() {
            _modelproto.initialize.apply(this,arguments);

            this.salesperson_name = null ;
        },



        load_salesperson: function(){
            var self = this;
            var def  = new $.Deferred();
            var fields = ['name'];
            new Model('hr.employee')
                .query(fields)
                .filter([['job_id','=','salesperson']])
                .all({'timeout':3000, 'shadow': true})

            return def;
        },
        fetch: function(model, fields, domain, ctx){
            this._load_progress = (this._load_progress || 0) + 0.05;
            this.chrome.loading_message(_t('Loading')+' '+model,this._load_progress);
            return new Model(model).query(fields).filter(domain).context(ctx).all()
        },
        set_salesperson_name: function(name){
            //this.set('salesperson_name', name);
            this.salesperson_name = name;
        },
        get_salesperson_name:function(){

            return this.salesperson_name;
        },
    });
    screens.ProductScreenWidget.include({

        start: function(){
            this._super(parent);
            var self = this;
            //this.cashpad = new CashierWidget(this,{});
            //this.cashpad.replace(this.$('.placeholder-CashierWidget'));

        },
        get_cur_pos_config_id: function(){
            var self = this;
            var config = self.pos.get('pos_config');
            var config_id = null;

            if(config){
                config_id = config.id;

                return config_id;
            }
            return '';
        },

        // fetch: function(model, fields, domain, ctx){
        //     return new instance.web.Model(model).query(fields).filter(domain).context(ctx).all()
        // },

        cashier_change: function(name){
            var self = this;
            globalCashier = name;

            self.pos.set_salesperson_name(name);

            var w =self.pos.get_salesperson_name();

            console.log('work :' + w);
            // $('#pay-screen-cashier-name').html(name);
            console.log('cashier_change : ' + name);

            // if(name != ''){
            //     $('.gotopay-button').removeAttr('disabled');
            // } else{
            //     $('.gotopay-button').attr('disabled', 'disabled');
            // }
        },

        get_cashiersd: function(){
            var self = this;
            var cashier_list = [];

            var loaded = self.pos.fetch('hr.employee',['name'],[['job_id','=','salesperson']])
                .then(function(cashiers){
                     for(var i = 0, len = cashiers.length; i < len; i++){
                        cashier_list.push(cashiers[i].name);

                     }

                    if(cashier_list.length > 0){

                        for(var i = 0, len = cashier_list.length; i < len; i++){
                            var content = self.$('#cashier-selected').html();
                            var new_option = '<option value="' + cashier_list[i] + '">' + cashier_list[i] + '</option>\n';
                            self.$('#cashier-selected').html(content + new_option);

                            }

                        // self.$('#AlertNoCashier').css('display', 'none');
                        self.$('#cashier-select').selectedIndex = 0;
                        globalCashier = cashier_list[0];
                        self.cashier_change(globalCashier);

                    } else{

                         //if there are no cashier
                        // self.$('#AlertNoCashier').css('display', 'block');
                        // self.$('.gotopay-button').attr('disabled', 'disabled');
                    }
                });
        },

        renderElement: function() {
            var self = this;
            this._super();

            self.$('#cashier-selected').change(function(){
                var name = this.value;
                self.cashier_change(name);

            });
        },

    });
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({

        initialize: function() {
            _super_order.initialize.apply(this,arguments);

            this.salesperson_name = this.pos.salesperson_id ;
	    console.log('atinit : ' + this.salesperson_name);
            this.save_to_db();
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            // json.table     = this.table ? this.table.name : undefined;
            // json.table_id  = this.table ? this.table.id : false;
            // json.floor     = this.table ? this.table.floor.name : false;
            // json.floor_id  = this.table ? this.table.floor.id : false;
            json.salesperson_name = this.pos.get_salesperson_name();
            console.log('atjaison : ' + json.salesperson_name);
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            // this.table = this.pos.tables_by_id[json.table_id];
            // this.floor = this.table ? this.pos.floors_by_id[json.floor_id] : undefined;
            this.salesperson_name = json.salesperson_name ;
	    console.log('atinitjaison : ' + this.salesperson_name);
        },
        // export_for_printing: function() {
        //     // var json = _super_order.export_for_printing.apply(this,arguments);
        //     // json.table = this.table ? this.table.name : undefined;
        //     // json.floor = this.table ? this.table.floor.name : undefined;
        //     json.customer_count = this.pos.get('selectedOrder').get_salesperson_name();
        //     return json;
        // },



    });




});