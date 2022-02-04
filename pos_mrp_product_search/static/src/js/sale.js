odoo.define('pos_mrp_saleprice_check.sale', function (require) {
var models = require('point_of_sale.models');
var core = require('web.core');
var _t = core._t;
var screens = require('point_of_sale.screens');

var SuperProductCategoriesWidget = screens.ProductCategoriesWidget;



    screens.ProductCategoriesWidget.include({
    init: function(parent, options){
        var self = this;
        this._super(parent,options);
    this.mrp_search_handler = function(event){

        self.search_product_basedon_article();
    };
    },

    search_product_basedon_article:function(){
        var self = this;
        var products;
        var query=this.el.querySelector('.searchbox input').value;
    // console.log(query);
    // var barcode= query;
        if(query){
            var article = parseInt(query)
            if (isNaN(article)){
                products = this.pos.db.get_product_by_category(this.category.id);
                this.product_list_widget.set_product_list(products);
                this.clear_search();
            }
            else{
                if (this.pos.db.product_by_id[article]){
                    products=this.pos.db.product_by_id[article]
                    this.pos.get_order().add_product(products);
                    this.clear_search();
                }
                else{
                    products = this.pos.db.get_product_by_category(this.category.id);
                    this.product_list_widget.set_product_list(products);
                    this.clear_search();
                }
            // products = this.pos.db.search_product_in_category(category.id,query);
            // if(products.length === 1){
            // this.pos.get_order().add_product(query);
            // this.clear_search();
            // }else{
            // this.product_list_widget.set_product_list(products);
            // }

            }

        }else{
            products = this.pos.db.get_product_by_category(this.category.id);
            this.product_list_widget.set_product_list(products);
            this.clear_search();

        }
        // self.pos.barcode_reader.scan(barcode);
        // this.pos.scan_product(barcode);

        },
    renderElement: function(){
        var self = this;
        this._super();
        this.el.querySelector('.mrp_search input').addEventListener('keypress',this.mrp_search_handler);

        this.el.querySelector('.mrp_search input').addEventListener('keydown',this.mrp_search_handler);

//        this.el.querySelector('.mrp_search').addEventListener('click',this.mrp_search_handler);
    // this.$('.article_search').click(function(event){
    // self.search_product_basedon_article(event);
    // });
    },

    });



});