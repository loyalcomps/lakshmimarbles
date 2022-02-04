odoo.define('qlty_product_available.MrpSearch',function(require){
"use_strict";
var POSDB = require('point_of_sale.DB');
//var _super_Db = models.PosDB.prototype;
POSDB.include({
    _product_search_string: function(product){
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
            str += '|' + mrp.concat(product.display_name)
            str  = product.id + ':' + str.replace(/:/g,'') + '\n';
            return str;

        }
        return this._super.apply(this,arguments);

    },
});

});