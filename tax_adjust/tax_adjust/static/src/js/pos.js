odoo.define('tax_adjust.Taxadjust', function(require){
"use strict";

    var utils = require('web.utils');

    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

    var models = require('point_of_sale.models');


    models.load_fields('account.tax','adjust_amount');
    models.load_fields('account.tax','cess_adjust_amount');

    var _super_orderline = models.Orderline.prototype;

    models.Orderline = models.Orderline.extend({

//        _compute_all: function(tax, base_amount, quantity) {
//            var taxs = _super_orderline._compute_all().apply(this,arguments)
//
//            if (tax.amount_type === 'percent' && tax.price_include){
//
//                if (tax.adjust_amount === 0.0){
//                    return base_amount - (base_amount / (1 + tax.amount / 100));
//                }
//                else{
//
//                    return (base_amount - (base_amount / (1 + tax.adjust_amount / 100)))/2;
//                }
//
//            }
//
//            return taxs;
//        },
//        _compute_all: function(tax, base_amount, quantity) {
//        if (tax.amount_type === 'fixed') {
//            var sign_base_amount = base_amount >= 0 ? 1 : -1;
//            return (Math.abs(tax.amount) * sign_base_amount) * quantity;
//        }
//        if ((tax.amount_type === 'percent' && !tax.price_include) || (tax.amount_type === 'division' && tax.price_include)){
//            return base_amount * tax.amount / 100;
//        }
//        if (tax.amount_type === 'percent' && tax.price_include){
//            if (tax.cess_adjust_amount === 0.0){
//                if (tax.adjust_amount === 0.0){
//                    return base_amount - (base_amount / (1 + tax.amount / 100));
//                }
//                else{
//
//                    return (base_amount - (base_amount / (1 + tax.adjust_amount / 100)))/2;
//                }
//            }
//            else{
//                if (tax.adjust_amount === 0.0 && tax.cess_adjust_amount === 0.0){
//                    return base_amount - (base_amount / (1 + tax.amount / 100));
//                }
//                else{
//
//                    return (base_amount - (base_amount / (1 + tax.adjust_amount / 100)))/tax.cess_adjust_amount;
//                }
//            }
//
//        }
//        if (tax.amount_type === 'division' && !tax.price_include) {
//            return base_amount / (1 - tax.amount / 100) - base_amount;
//        }
//        return false;
//        },
    });










});
