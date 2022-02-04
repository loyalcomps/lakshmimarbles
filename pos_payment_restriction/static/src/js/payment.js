odoo.define('pos_payment_restriction.payment', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var utils = require('web.utils');
    var Model = require('web.DataModel');

    var QWeb = core.qweb;
    var _t = core._t;
    var round_pr = utils.round_precision;

    var _super_posmodel = models.PosModel.prototype;


    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({

//        var s=1;
        add_paymentline: function(cashregister) {
            //debugger;
            this.assert_editable();
            var self = this;
            var journal = cashregister.journal;

            var newPaymentline = new models.Paymentline({}, {
                order: this,
                cashregister: cashregister,
                pos: this.pos
            });
            var flag = false;
            if (cashregister.journal.type !== 'cash' || this.pos.config.iface_precompute_cash){
                 newPaymentline.set_amount(this.get_due());
            }

           if (this.get_due() == 0)
                 {
                 alert("You can't add payment line as the amount is already fullfilled")
                 flag = true;
                 }
           var lines = this.paymentlines.models;
                for (var i = 1; i < lines.length; i++) {
                    var a=lines[i].get_amount();
                    if (a === 0) {
                        alert("You can't add payment line as the amount is already fullfilled")
                       flag = true;
                    }
                }
            if(flag == false)
                {
                   this.paymentlines.add(newPaymentline);
                   this.select_paymentline(newPaymentline);
                }

        },

    });



});