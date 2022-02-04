
odoo.define('pos_mrp_product_search.mrp_product', function (require) {
//    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;
    var screens = require('point_of_sale.screens');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var popups = require("point_of_sale.popups");
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var PosDB = require("point_of_sale.DB");
    var PosBaseWidget = require('point_of_sale.BaseWidget');

    var utils = require('web.utils');

    var QWeb = core.qweb;

//    var models = require('point_of_sale.models');
//    var _super_posmodel = models.PosModel.prototype;
//
//    models.PosModel = models.PosModel.extend({
//        initialize: function (session, attributes) {
//            // New code
//            var partner_model = _.find(this.models, function(model){
//                return model.model === 'product.product';
//            });
//            partner_model.fields.push('barcode_ids');
//
//            // Inheritance
//            return _super_posmodel.initialize.call(this, session, attributes);
//        },
//    });
    var models = require('point_of_sale.models');
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function(model){ return model.model === 'product.product'; });
            partner_model.fields.push('barcode_ids');

            return _super_posmodel.initialize.call(this, session, attributes);
        },
    });

    PosDB.include({



        init: function(options){
            var self = this;
            this._super(options);
            options = options || {};
            this.name = options.name || this.name;
            this.limit = options.limit || this.limit;

            this.product_mrp_search_string = {};
        },



        mrp_product_search_string: function(product){

            var str;
            var str1;
            if (product.product_mrp){
                str = product.display_name;


                var mrp = product.product_mrp.toString();
                str += '%' + mrp.concat("&&"+product.display_name)+"**"+product.id;
                str  = product.id + ':' + str.replace(/:/g,'') + '\n';
//                return str;

            }

            else {
                str = product.display_name;
                var mrp = "0";
                str += '%'+  mrp.concat("&&"+product.display_name)+"**"+product.id;
                str  = product.id + ':' + str.replace(/:/g,'') + '\n';
//                return str;

            }
            if (product.barcode_ids){
                for(var i = 0, len = product.barcode_ids.length; i < len; i++){
                    var multi_barcode_id = product.barcode_ids[i];
                    if (!this.multi_barcode_by_id[multi_barcode_id]) {
                        continue
                    }
                    var multi_barcode=this.multi_barcode_by_id[multi_barcode_id]
                    str1 = product.display_name;
                    var mrp = multi_barcode.product_mrp.toString();
                    str1 += '%' + mrp.concat("&&"+product.display_name)+"**"+product.id;
                    str1 = product.id + ':' + str1.replace(/:/g,'') + '\n';
                    str += str1
                }



//                return str;

            }

            return str
        },


        mrp_search_product_in_category: function(category_id, query){
            var results = [];
            var price;
            var mrp_price;
            var pname;
            if (query){
                query=query.replace('*','=');
                price = query.split("=");
                mrp_price  =price[0];
                pname= price[1];
            }
            if (pname){
                pname.toLowerCase();
            }

            var d;
            var e;
            var h;
            var u;
            var mrp;
            var s= (this.product_mrp_search_string[category_id].split("\n"))
            for(var i = 0; i < s.length; i++){

                if (s[i]){
                    d = s[i].split("%");
                }
                else{
                    return results;
                }

                e= d[0];
                h=d[1];
                if (h){
                    u= h.split("&&");
                }

                mrp = u[0];
                if(u.length>=2){
                   var g= u[1].split("**");
                   var o = g[0];
                    var w = g[1];

                }
                else{
                    var o = "";
                    var w = "";
                }
                if (o){
                    o=o.toLowerCase();
                }

                if (mrp==mrp_price && o.startsWith(pname))
                {

                    var id = w;
                   results.push(this.get_product_by_id(id));

                }
                if(!mrp_price && pname!="" && o.startsWith(pname)){
                    var id = w;
                   results.push(this.get_product_by_id(id));
                }

                else{
                    continue;
                }
            }
            return results;
        },


        add_products: function(products){

            var self = this;
            this._super(products);
            var stored_categories = this.product_by_category_id;

            if(!products instanceof Array){
                products = [products];
            }
            for(var i = 0, len = products.length; i < len; i++){
                var product = products[i];
                var search_string = this.mrp_product_search_string(product);
                var categ_id = product.pos_categ_id ? product.pos_categ_id[0] : this.root_category_id;
                product.product_tmpl_id = product.product_tmpl_id[0];

                if(this.product_mrp_search_string[categ_id] === undefined){
                    this.product_mrp_search_string[categ_id] = '';
                }
                this.product_mrp_search_string[categ_id] += search_string;

                var ancestors = this.get_category_ancestors_ids(categ_id) || [];

                for(var j = 0, jlen = ancestors.length; j < jlen; j++){
                    var ancestor = ancestors[j];

                    if( this.product_mrp_search_string[ancestor] === undefined){
                        this.product_mrp_search_string[ancestor] = '';
                    }
                    this.product_mrp_search_string[ancestor] += search_string;
                }

            }
    },

});





    var SuperProductScreenWidget = screens.ProductScreenWidget;
    screens.ProductScreenWidget.include({

//
        init: function(parent, options){
            var self = this;
            this._super(parent,options);
            this.category = this.pos.root_category;
            this.start_categ_id = this.pos.config.iface_start_categ_id ? this.pos.config.iface_start_categ_id[0] : 0;

            this.set_category(this.pos.db.get_category_by_id(this.start_categ_id));


            var search_timeout  = null;

            this.mrp_search_handler = function(event){
                if(event.type == "keypress" || event.keyCode === 46 || event.keyCode === 8){
                    clearTimeout(search_timeout);

                    var searchbox = this;

                    search_timeout = setTimeout(function(){
                        self.mrp_perform_search(self.category,searchbox.value, event.which === 13);
                    },70);
                }
            };

            this.clears_search_handler = function(event){
            self.clear_mrp_search();
        };
    },
    click_product: function(product) {
        var self = this;
        var list=[]
        if(product.barcode_ids.length!=0){
            var selectedOrder = this.pos.get_order();
            if (selectedOrder) {
                if (product.barcode) {
                    var list = [{
                        'label': product['display_name']    + '| MRP: ' + product['product_mrp'] +
                        '| PRICE: ' + product['list_price'] + ' | QTY: 1 ' + '| and Uoms: ' + product['uom_id'][1],
                        'item': product,
                    }];
                }
                for (var i = 0; i < product.barcode_ids.length; i++) {
                    var barcode = this.pos.db.multi_barcode_by_id[product.barcode_ids[i]];
                    list.push({
                        'label': barcode['product_id'][1]   + '| MRP: ' + barcode['product_mrp'] + '| PRICE: ' + barcode['list_price'] + ' | QTY: ' + barcode['quantity'] + '| and Uoms: ' + barcode['uom_id'][1],
                        'item': barcode,
                    });
                }
                this.gui.show_popup('selection', {
                    title: _t('Select product'),
                    list: list,
                    confirm: function (item) {
                        var barcode;
                        var product;
                        if (item['product_id']) {
                            barcode = item;
                            product = self.pos.db.product_by_id[barcode.product_id[0]]
                            selectedOrder.add_product(product, {
                                product_mrp: barcode['product_mrp'],
                                price: barcode['list_price'],
                                quantity: barcode['quantity'],
                                barcode_id:barcode['id'],
                                barcode_price:barcode['list_price'],
                                extras: {
                                    uom_id: barcode['uom_id'][0]
                                }
                            });
                        } else {
                            product = item;
                            selectedOrder.add_product(product, {});
                        }
                    }
                });
            }
            console.log('hi');
        }
        else{
          this._super(product);
        }


    },

        renderElement: function(){
        var self = this;
        this._super();
        this.el.querySelector('.searchboxs input').addEventListener('keypress',this.mrp_search_handler);

        this.el.querySelector('.searchboxs input').addEventListener('keydown',this.mrp_search_handler);

        this.el.querySelector('.search-clears').addEventListener('click',this.clears_search_handler);


//        this.el.querySelector('.searchboxs ').addEventListener('click',this.articleproduct_search_handler);
        // this.$('.article_search').click(function(event){
        // self.search_product_basedon_article(event);
        // });
        },

        clear_mrp_search: function(){
        var products = this.pos.db.get_product_by_category(this.category.id);
        this.product_list_widget.set_product_list(products);
        var input = this.el.querySelector('.searchboxs input');
            input.value = '';
            input.focus();
    },



        mrp_perform_search: function(category, query, buy_result){
            var products;
            if(query){
                products = this.pos.db.mrp_search_product_in_category(category.id,query);
                if(buy_result && products.length === 1){
//                        this.pos.get_order().add_product(products[0]);
//                        this.clear_mrp_search();
                        this.product_list_widget.set_product_list(products);
                }else{
                    this.product_list_widget.set_product_list(products);
                }
            }else{
                products = this.pos.db.get_product_by_category(this.category.id);
                this.product_list_widget.set_product_list(products);
            }
    },

       set_category : function(category){
        var db = this.pos.db;
        if(!category){
            this.category = db.get_category_by_id(db.root_category_id);
        }else{
            this.category = category;
        }
        this.breadcrumb = [];
        var ancestors_ids = db.get_category_ancestors_ids(this.category.id);
        for(var i = 1; i < ancestors_ids.length; i++){
            this.breadcrumb.push(db.get_category_by_id(ancestors_ids[i]));
        }
        if(this.category.id !== db.root_category_id){
            this.breadcrumb.push(this.category);
        }
        this.subcategories = db.get_category_by_id(db.get_category_childs_ids(this.category.id));
    },

        });
        });