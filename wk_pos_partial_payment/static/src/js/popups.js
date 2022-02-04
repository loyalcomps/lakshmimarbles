/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('wk_pos_partial_payment.popups', function (require) {
    "use strict";

    var gui = require('point_of_sale.gui');
    var popup_widget = require('point_of_sale.popups');

    var PartialPaymentBlockPopup = popup_widget.extend({
        template:'PartialPaymentBlockPopup',
    });
    gui.define_popup({name:'partial_payment_block', widget: PartialPaymentBlockPopup});
});