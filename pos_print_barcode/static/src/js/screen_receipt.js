odoo.define('pos_print_barcode.screen_receipt_ean', function (require) {
"use strict";
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var _t = core._t;
    var gui = require('point_of_sale.gui');
    var rpc = require('pos.rpc');
    var qweb = core.qweb;

    screens.ReceiptScreenWidget.include({

        show: function () {
            this._super();
            try {
                if (this.pos.config.barcode_receipt) {
                    var order = this.pos.get_order();
                    JsBarcode("#barcode", order['ean13_barcode'], {
                        format: "EAN13",
                        displayValue: true,
                        fontSize: 20
                    });
                }
            } catch (error) {
                console.error(error)
            }
        },

    });

});
