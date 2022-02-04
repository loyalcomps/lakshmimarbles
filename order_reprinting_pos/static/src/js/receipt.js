odoo.define('order_reprinting_pos.receipt',function(require) {
"use strict";
var gui = require('point_of_sale.gui');
var chrome = require('point_of_sale.chrome');
var popups = require('point_of_sale.popups');
var core = require('web.core');
var models = require('point_of_sale.models');
var PosModelSuper = models.PosModel;
var pos_screens = require('point_of_sale.screens');
var Model = require('web.DataModel');
var QWeb = core.qweb;
var _t = core._t;
var screens = require('point_of_sale.screens');


var ReprintTicketScreenWidget = screens.ScreenWidget.extend({
        template: 'ReprintTicketScreenWidget',
        show: function() {
            var self = this;
            self._super();
            $('.button.back').on("click", function() {
                self.gui.show_screen('products');
            });
            $('.button.next').on("click", function() {
                self.gui.show_screen('products');
            });
            $('.button.print').click(function() {
                var test = self.chrome.screens.receipt;
                setTimeout(function() {
                    self.chrome.screens.receipt.lock_screen(false);
                }, 1000);
                if (!test['_locked']) {
                    self.chrome.screens.receipt.print_web();
                    self.chrome.screens.receipt.lock_screen(true);
                }
            });
        }
    });
    gui.define_screen({ name: 'reprint_ticket', widget: ReprintTicketScreenWidget });

});