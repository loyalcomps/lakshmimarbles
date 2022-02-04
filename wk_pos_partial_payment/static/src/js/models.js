/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('wk_pos_partial_payment.models', function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var SuperOrder = models.Order.prototype;

    models.load_fields('res.partner', ['property_payment_term_id','prevent_partial_payment']);

    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            SuperOrder.initialize.call(this, attributes, options);
            this.invoice_remark = '';
            this.is_partially_paid = false;
        },
        export_as_JSON: function(){
            var order_json = SuperOrder.export_as_JSON.call(this);
            order_json.invoice_remark = this.invoice_remark;
            order_json.is_partially_paid = this.is_partially_paid;
            return order_json;
        },
    });
});