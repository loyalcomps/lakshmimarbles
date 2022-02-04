"use strict";
/*
    This module create by: thanhchatvn@gmail.com
    License: OPL-1
    Please do not modification if i not accept
    Thanks for understand
 */
odoo.define('pos_print_barcode.order', function (require) {

    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({

        init_from_JSON: function (json) {
            var res = _super_Order.init_from_JSON.apply(this, arguments);

            if (json.ean13_barcode) {
                this.ean13_barcode = json.ean13_barcode;
            }

            return res;
        },
        export_as_JSON: function () {
            var json = _super_Order.export_as_JSON.apply(this, arguments);

            if (this.ean13_barcode) {
                json.ean13_barcode = this.ean13_barcode;
            }
            if (!this.ean13_barcode && this.uid) {
                var ean13 = '998';
                if (this.pos.user.id) {
                    ean13 += this.pos.user.id;
                }
                if (this.sequence_number) {
                    ean13 += this.sequence_number;
                }
                if (this.pos.config.id) {
                    ean13 += this.pos.config.id;
                }
                var format_ean13 = this.uid.split('-');
                for (var i in format_ean13) {
                    ean13 += format_ean13[i];
                }
                ean13 = ean13.split("");
                var ean13_array = []
                var ean13_str = ""
                for (var i = 0; i < ean13.length; i++) {
                    if (i < 12) {
                        ean13_str += ean13[i]
                        ean13_array.push(ean13[i])
                    }
                }
                this.ean13_barcode = ean13_str + this.generate_unique_ean13(ean13_array).toString()
            }

            return json;
        },

        generate_unique_ean13: function (array_code) {
            if (array_code.length != 12) {
                return -1
            }
            var evensum = 0;
            var oddsum = 0;
            for (var i = 0; i < array_code.length; i++) {
                if ((i % 2) == 0) {
                    evensum += parseInt(array_code[i])
                } else {
                    oddsum += parseInt(array_code[i])
                }
            }
            var total = oddsum * 3 + evensum
            return parseInt((10 - total % 10) % 10)
        },

    });


});

odoo.define('pos_print_barcode.receipt_screen', function(require) {
    "use strict";
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var ReceiptScreenWidget = screens.ReceiptScreenWidget;
    ReceiptScreenWidget.include({
        show: function() {
            this._super();
            try {
                if (this.pos.config.barcode_receipt) {
                    var order = this.pos.get_order();
                    JsBarcode("#barcode", order['ean13_barcode'], {
                        format: "EAN13",
                        displayValue: true,
                        fontSize: 12,
//                        width:4,
                        height:25
                    });
                }
            } catch (error) {
                console.error(error)
            }
        },

    });
});
