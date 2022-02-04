odoo.define('kerala_flood_cess.pos', function(require){
"use strict";

    var utils = require('web.utils');

    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

    var models = require('point_of_sale.models');


//    models.load_fields('res.partner',['x_gstin','partner_type']);

    models.load_fields('account.tax','kfc_adjust_amount');
    models.load_fields('account.tax','kfc_cess_adjust_amount');
    models.load_fields('account.tax','kfc');

    var _super_orderline = models.Orderline.prototype;

    models.Orderline = models.Orderline.extend({




       compute_all: function(taxes, price_unit, quantity, currency_rounding, no_map_tax) {
//        var pos_res_partner = this.pos.get_client() ? this.pos.get_client().name : null ;
        var res_partner = this.order.get_client();
        var self = this;
        var list_taxes = [];
        var currency_rounding_bak = currency_rounding;
        if (this.pos.company.tax_calculation_rounding_method == "round_globally"){
           currency_rounding = currency_rounding * 0.00001;
        }
        var total_excluded = round_pr(price_unit * quantity, currency_rounding);
        var total_included = total_excluded;
        var base = total_excluded;
        _(taxes).each(function(tax) {
            if (!no_map_tax){
                tax = self._map_tax_fiscal_position(tax);
            }
            if (!tax){
                return;
            }
            if (tax.amount_type === 'group'){






                 if (res_partner){


                    if (res_partner.partner_type==="B2B" && tax.name !='GST 28% + Cess 12%')
    //

                     {

                        var ret = self.compute_all(tax.children_tax_ids.slice(0,2), price_unit, quantity, currency_rounding);
                        total_excluded = ret.total_excluded;
                        base = ret.total_excluded;
                        total_included = ret.total_included;
                        list_taxes = list_taxes.concat(ret.taxes);


                     }

                      else if (res_partner.partner_type==="B2B" && tax.name ==='GST 28% + Cess 12%')
    //

                     {

                        var ret = self.compute_all(tax.children_tax_ids.slice(0,3), price_unit, quantity, currency_rounding);
                        total_excluded = ret.total_excluded;
                        base = ret.total_excluded;
                        total_included = ret.total_included;
                        list_taxes = list_taxes.concat(ret.taxes);


                     }

                      else if (res_partner.partner_type==="IMPORT" && tax.name!="GST 28% + Cess 12%")
    //                 && tax.name !='GST 28% + Cess 12%'

                     {

                        var ret = self.compute_all(tax.children_tax_ids.slice(0,2), price_unit, quantity, currency_rounding);
                        total_excluded = ret.total_excluded;
                        base = ret.total_excluded;
                        total_included = ret.total_included;
                        list_taxes = list_taxes.concat(ret.taxes);


                     }

                      else if (res_partner.partner_type==="IMPORT" && tax.name==="GST 28% + Cess 12%")
    //                 && tax.name !='GST 28% + Cess 12%'

                     {

                        var ret = self.compute_all(tax.children_tax_ids.slice(0,3), price_unit, quantity, currency_rounding);
                        total_excluded = ret.total_excluded;
                        base = ret.total_excluded;
                        total_included = ret.total_included;
                        list_taxes = list_taxes.concat(ret.taxes);


                     }

                     else{

                        if (res_partner.x_gstin===false)
                            {

                            var ret = self.compute_all(tax.children_tax_ids, price_unit, quantity, currency_rounding);
                            total_excluded = ret.total_excluded;
                            base = ret.total_excluded;
                            total_included = ret.total_included;
                            list_taxes = list_taxes.concat(ret.taxes);

                            }

                        else

                        {

                            var ret = self.compute_all(tax.children_tax_ids, price_unit, quantity, currency_rounding);
                            total_excluded = ret.total_excluded;
                            base = ret.total_excluded;
                            total_included = ret.total_included;
                            list_taxes = list_taxes.concat(ret.taxes);
                        }




                     }




}


            else


            {


//            if (res_partner===null)
//
//
////                 && tax.name !='GST 28% + Cess 12%'
//
//                 {


                    var ret = self.compute_all(tax.children_tax_ids, price_unit, quantity, currency_rounding);
                    total_excluded = ret.total_excluded;
                    base = ret.total_excluded;
                    total_included = ret.total_included;
                    list_taxes = list_taxes.concat(ret.taxes);

//                 }



            }

            }
            else {
                var tax_amount = self._compute_all(tax, base, quantity);
                tax_amount = round_pr(tax_amount, currency_rounding);

                if (tax_amount){
                    if (tax.price_include) {
                        total_excluded -= tax_amount;
                        base -= tax_amount;
                    }
                    else {
                        total_included += tax_amount;
                    }
                    if (tax.include_base_amount) {
                        base += tax_amount;
                    }
                    var data = {
                        id: tax.id,
                        amount: tax_amount,
                        name: tax.name,
                    };
                    list_taxes.push(data);
                }
            }
        });
        return {
            taxes: list_taxes,
            total_excluded: round_pr(total_excluded, currency_rounding_bak),
            total_included: round_pr(total_included, currency_rounding_bak)
        };
    },

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
        _compute_all: function(tax, base_amount, quantity) {

//        var partner = this.pos.partners;
        var res_partner = this.order.get_client() ;
//        var pos_res_partner = this.pos.get_client() ? this.pos.get_client().name : null ;



        if (tax.amount_type === 'fixed') {
            var sign_base_amount = base_amount >= 0 ? 1 : -1;
            return (Math.abs(tax.amount) * sign_base_amount) * quantity;
        }
        if ((tax.amount_type === 'percent' && !tax.price_include) || (tax.amount_type === 'division' && tax.price_include)){
            return base_amount * tax.amount / 100;
        }
        if (tax.amount_type === 'percent' && tax.price_include){


                if(res_partner === null){


                    if (tax.kfc_cess_adjust_amount!=0.0 && tax.kfc_adjust_amount!=0.0){


                        if (tax.kfc_cess_adjust_amount === 0.0){
                            if (tax.kfc_adjust_amount === 0.0){
                                return base_amount - (base_amount / (1 + tax.amount / 100));
                            }
                            else{

                                return (base_amount - (base_amount / (1 + tax.kfc_adjust_amount / 100)))/2;
                            }
                        }
                        else{
                            if (tax.kfc_adjust_amount === 0.0 && tax.kfc_cess_adjust_amount === 0.0){
                                return base_amount - (base_amount / (1 + tax.amount / 100));
                            }
                            else{

                                return (base_amount - (base_amount / (1 + tax.kfc_adjust_amount / 100)))/tax.kfc_cess_adjust_amount;
                            }
                        }
                        }

                    else{
                        if (tax.cess_adjust_amount === 0.0){
                            if (tax.adjust_amount === 0.0){
                                return base_amount - (base_amount / (1 + tax.amount / 100));
                            }
                            else{

                                return (base_amount - (base_amount / (1 + tax.adjust_amount / 100)))/2;
                            }
                        }
                        else{
                            if (tax.adjust_amount === 0.0 && tax.cess_adjust_amount === 0.0){
                                return base_amount - (base_amount / (1 + tax.amount / 100));
                            }
                            else{

                                return (base_amount - (base_amount / (1 + tax.adjust_amount / 100)))/tax.cess_adjust_amount;
                            }
                        }
                }


                }



                else if(res_partner.x_gstin === false){

                    if (tax.kfc_cess_adjust_amount!=0.0 && tax.kfc_adjust_amount!=0.0){


                        if (tax.kfc_cess_adjust_amount === 0.0){
                            if (tax.kfc_adjust_amount === 0.0){
                                return base_amount - (base_amount / (1 + tax.amount / 100));
                            }
                            else{

                                return (base_amount - (base_amount / (1 + tax.kfc_adjust_amount / 100)))/2;
                            }
                        }
                        else{
                            if (tax.kfc_adjust_amount === 0.0 && tax.kfc_cess_adjust_amount === 0.0){
                                return base_amount - (base_amount / (1 + tax.amount / 100));
                            }
                            else{

                                return (base_amount - (base_amount / (1 + tax.kfc_adjust_amount / 100)))/tax.kfc_cess_adjust_amount;
                            }
                        }
                        }

                    else{
                        if (tax.cess_adjust_amount === 0.0){
                            if (tax.adjust_amount === 0.0){
                                return base_amount - (base_amount / (1 + tax.amount / 100));
                            }
                            else{

                                return (base_amount - (base_amount / (1 + tax.adjust_amount / 100)))/2;
                            }
                        }
                        else{
                            if (tax.adjust_amount === 0.0 && tax.cess_adjust_amount === 0.0){
                                return base_amount - (base_amount / (1 + tax.amount / 100));
                            }
                            else{

                                return (base_amount - (base_amount / (1 + tax.adjust_amount / 100)))/tax.cess_adjust_amount;
                            }
                        }
                }






                }



                else{
                    if (tax.cess_adjust_amount === 0.0){
                        if (tax.adjust_amount === 0.0){
                            return base_amount - (base_amount / (1 + tax.amount / 100));
                        }
                        else{

                            return (base_amount - (base_amount / (1 + tax.adjust_amount / 100)))/2;
                        }
                    }
                    else{
                        if (tax.adjust_amount === 0.0 && tax.cess_adjust_amount === 0.0){
                            return base_amount - (base_amount / (1 + tax.amount / 100));
                        }
                        else{

                            return (base_amount - (base_amount / (1 + tax.adjust_amount / 100)))/tax.cess_adjust_amount;
                        }
                    }
                }






        }
        if (tax.amount_type === 'division' && !tax.price_include) {
            return base_amount / (1 - tax.amount / 100) - base_amount;
        }
        return false;
        },
    });










});
