odoo.define('pos_order_reprint.pos_order_reprint', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var Model = require('web.DataModel');
    var core = require('web.core');
    var ActionManager = require('web.ActionManager');
    var pos_orders = require('pos_orders.pos_orders');

    var QWeb = core.qweb;
    var _t = core._t;

    models.load_fields('pos.config', 'wk_reprint_type');

    var ReprintTicketScreenWidget = screens.ScreenWidget.extend({
        template: 'ReprintTicketScreenWidget',
        show: function() {
            var self = this;
            self._super();
            $('.button.back.wk_back_reprint').on("click", function() {
                self.gui.show_screen('wk_order');
            });
            $('.button.back.wk_home_reprint').on("click", function() {
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

    pos_orders.include({
        show: function() {
            var self = this;
            self._super();

            this.$('.wk-order-list-contents').delegate('.wk_print_content', 'click', function(event){
                var order_id = parseInt(this.id);
                if(self.pos.config.wk_reprint_type != 'pdf'){
                    (new Model('pos.order')).call('get_report_data', [{ 'order_id': order_id }])
                    .then(function(result) {
                        var cashier = self.pos.cashier || self.pos.user;
                        var company = self.pos.company;
                        result['pos'] = self.pos;
                        result['receipt']['header'] = self.pos.config.receipt_header || '';
                        result['receipt']['footer'] = self.pos.config.receipt_footer || '';
                        result['receipt']['curr_user'] = cashier ? cashier.name : null
                        result['receipt']['shop'] = self.pos.shop;
                        result['receipt']['company'] = {
                            email: company.email,
                            website: company.website,
                            company_registry: company.company_registry,
                            contact_address: company.partner_id[1],
                            vat: company.vat,
                            name: company.name,
                            phone: company.phone,
                            logo: self.pos.company_logo_base64,
                        };
                        result['receipt']['date'] = {
                            localestring: result['receipt']['date'],
                        };

                        if (self.pos.config.wk_reprint_type == 'ticket') {
                            $('.pos-receipt-container').html(QWeb.render('webkulPosTicket', {
                                widget: self,
                                receipt: result.receipt,
                            }));
                            self.gui.show_screen("reprint_ticket");
                        } else {
                            var receipt = QWeb.render('webkulXmlReceipt', result);
                            self.pos.proxy.print_receipt(receipt);
                        }
                    });
                }
                else{
                    (new Model('pos.order').call('reprint_receipt'))
                    .then(function(result){
                        this.action_manager = new ActionManager(this);
                        this.action_manager.do_action(result, {
                            additional_context: {
                                active_id: order_id,
                                active_ids: [order_id],
                                active_model: 'pos.order'
                            }
                        });
                    })
                    .fail(function (error, event){
                        self.gui.show_popup('error',{
                        'title': _t("Error!!!"),
                        'body':  _t("Check your internet connection and try again."),
                        });
                        event.preventDefault();
                    });
                }
            });

        }
    });
});
