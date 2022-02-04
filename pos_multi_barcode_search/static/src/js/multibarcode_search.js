odoo.define('pos_multi_barcodes.product_search', function (require) {
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;
    var screens = require('point_of_sale.screens');

    var SuperProductScreenWidget = screens.ProductScreenWidget;



    screens.ProductScreenWidget.include({
        events:_.extend({},SuperProductScreenWidget.prototype.events,{
			'click .wk_tag': 'search_multi_barcode',
//			'change .searchbox-multi-barcode':'search_multi_barcode',

		}),
//		select_product_tag:function(event){
//		    var self = this;
//		    console.log(this.$('input.searchbox-multi-barcode').val());
//
//		},
		search_multi_barcode:function(event){
		    var self = this;
		    console.log(this.$('input.searchbox-multi-barcode').val());
		    var barcode= this.$('input.searchbox-multi-barcode').val();
		    self.pos.barcode_reader.scan(barcode);
//		    this.pos.scan_product(barcode);

		},

	});



});