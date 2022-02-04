
odoo.define('pos_mrp_saleprice_check.sale_price', function (require) {
    var models = require('point_of_sale.models');
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


    var SuperProductScreenWidget = screens.ProductScreenWidget;



    screens.ProductScreenWidget.include({
        events:_.extend({},SuperProductScreenWidget.prototype.events,{
			'click .search': 'searchbox-mrp',
//			'change .searchbox-multi-barcode':'search_multi_barcode',


		}),

		start: function () {
            var self = this;
            this._super();

//            this.products = this.pos.database['product.product'];
            this.product_by_id = {};
            this.product_by_string = "";
            if (this.products) {
                this.save_products(this.products);
            }
        },

        init: function (parent, options) {
            var self = this;
            this._super(parent, options);
            this.product_cache = new screens.DomCache();
            this.category_mrp_search_string = {};
            this.product_list = options.product_list || [];

            this.pos.bind('sync:product', function (product_data) { // product operation update screen
                var products = _.filter(this.pos.database['product.product'], function (product) {
                    return product['id'] != product_data['id'];
                });
                products.push(product_data);
                self.product_by_id[product_data['id']] = product_data;
                self.product_by_string +=this._product_mrp_search_string(product_data);
                self.clear_search();
                self.display_product_edit('show', product_data);
            });
        },


        add_products: function(products){
            var self = this;
            this._super();
            var stored_categories = this.product_by_category_id;

            if(!products instanceof Array){
                products = [products];
            }
            for(var i = 0, len = products.length; i < len; i++){
                var product = products[i];
                var search_string = this._product_mrp_search_string(product);
                var categ_id = product.pos_categ_id ? product.pos_categ_id[0] : this.root_category_id;
                product.product_tmpl_id = product.product_tmpl_id[0];
                if(!stored_categories[categ_id]){
                    stored_categories[categ_id] = [];
                }
                stored_categories[categ_id].push(product.id);

                if(this.category_search_string[categ_id] === undefined){
                    this.category_search_string[categ_id] = '';
                }
                this.category_search_string[categ_id] += search_string;

                if(this.category_mrp_search_string[categ_id] === undefined){
                    this.category_mrp_search_string[categ_id] = '';
                }
                this.category_mrp_search_string[categ_id] += search_string;

                var ancestors = this.get_category_ancestors_ids(categ_id) || [];

                for(var j = 0, jlen = ancestors.length; j < jlen; j++){
                    var ancestor = ancestors[j];
                    if(! stored_categories[ancestor]){
                        stored_categories[ancestor] = [];
                    }
                    stored_categories[ancestor].push(product.id);

                    if( this.category_search_string[ancestor] === undefined){
                        this.category_search_string[ancestor] = '';
                    }
                    this.category_search_string[ancestor] += search_string;

                     if( this.category_mrp_search_string[ancestor] === undefined){
                        this.category_mrp_search_string[ancestor] = '';
                    }
                    this.category_mrp_search_string[ancestor] += search_string;
                }
                this.product_by_id[product.id] = product;
                if(product.barcode){
                    this.product_by_barcode[product.barcode] = product;
                }
            }
        },


        _product_mrp_search_string: function(product){
            if (product.product_mrp){
                var str = product.display_name;
                if (product.barcode) {
                    str += '|' + product.barcode;
                }
                if (product.default_code) {
                    str += '|' + product.default_code;
                }
                if (product.description) {
                    str += '|' + product.description;
                }
                if (product.description_sale) {
                    str += '|' + product.description_sale;
                }
                var mrp = product.product_mrp.toString();
                str += '%' + mrp.concat("&"+product.display_name)
                str  = product.id + ':' + str.replace(/:/g,'') + '\n';
                return str;

            }
            else{

                var str = product.display_name;
                if (product.barcode) {
                    str += '|' + product.barcode;
                }
                if (product.default_code) {
                    str += '|' + product.default_code;
                }
                if (product.description) {
                    str += '|' + product.description;
                }
                if (product.description_sale) {
                    str += '|' + product.description_sale;
                }

                var mrp = "";
                str += '%' + mrp.concat("&"+product.display_name)
                str  = product.id + ':' + str.replace(/:/g,'') + '\n';
                return str;

            }
            return this._super.apply(this,arguments);

        },



         save_products: function (products) {


            var products = this.pos.products;

            for (var i = 0; i < 100; i++) {
                var product = this.products
                this.pos.db.get_product_by_category(this.category.id);
                this.product_list_widget.set_product_list(products);
                this.product_by_id[product['id']] = product;
                this.product_by_string += this._product_mrp_search_string(product);
            }

            return
        },


		search_mrp_products: function (query,categ_id) {
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g, '.');
                query = query.replace(' ', '.+');
                var re = RegExp("([0-9]+):.*?" + query, "gi");
            } catch (e) {
                return [];
            }
            var results = [];
            for (var i = 0; i < 1000; i++) {
                this.pos.db.get_product_by_category(this.category.id);
                this.product_list_widget.set_product_list(products);

                var r = re.exec(this.category_mrp_search_string[this.category.id]);
                    if(r){

                        var id = Number(r[1]);
                        results.push(this.get_product_by_id(id));
//                        var id = Number(r[1]);
//                        results.push(this.get_product_by_id(id));
//                        full_name = r.input.split("%")
//                        mrp_part = full_name[1].split("&")
//                        mrp_price  = mrp_part[0]
//                        mrp_name = mrp_part[1]
//                        querymrp=query.split(".")
//                        mrp=querymrp[0]
//                        name = querymrp[1]
//                        if (mrp==mrp_price && name.startsWith(mrp_name)){
//
//                            var id = Number(r[1]);
//                            results.push(this.get_product_by_id(id));
//                        }

                        }


                    else {
                            break;
                        }


                }
                return results;
        },



		search_mrp:function(event){
		    this.category = this.pos.root_category;
		    var self = this;
		    console.log(this.$('input.searchbox-mrp').val());
		    var mrp= this.$('input.searchbox-mrp').val();
		    var search;
            var search = this.search_mrp_products(mrp,self.categ_id);

            if(mrp){
                products = this.search_mrp_products(mrp,self.categ_id)

        }
//            this.products_last_search = products;
//            this.render_list(products);
//		    self.pos.barcode_reader.scan(barcode);
//		    this.pos.scan_product(barcode);

		},

	});


});