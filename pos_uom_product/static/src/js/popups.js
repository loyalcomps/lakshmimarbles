odoo.define('pos_retail.popups', function (require) {

    var core = require('web.core');
    var _t = core._t;
    var gui = require('point_of_sale.gui');
    var PopupWidget = require('point_of_sale.popups');
    var rpc = require('web.rpc');
    var qweb = core.qweb;




     var alert_result = PopupWidget.extend({
        template: 'alert_result',
        show: function (options) {
            var self = this;
            if (options) {
                swal({
                    title: options.title,
                    text: options.body,
                    buttonsStyling: false,
                    confirmButtonClass: "btn btn-info",
                    timer: options.timer || 1500
                }).catch(swal.noop)
            }
            this._super(options);
            $('.swal2-confirm').click(function () {
                self.click_confirm();
            });
            $('.swal2-cancel').click(function () {
                self.click_cancel();
            })
        }
    });
    gui.define_popup({name: 'alert_result', widget: alert_result});

    });