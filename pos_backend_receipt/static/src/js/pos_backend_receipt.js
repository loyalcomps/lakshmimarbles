odoo.define("pos_backend_receipt.pos_backend_receipt",function (require) {

    var core = require('web.core');
    var FormView = require('web.FormView');
    var Model = require('web.DataModel');
    var Session = require('web.Session');
    var framework = require('web.framework');

    var QWeb = core.qweb;
    var _t = core._t;

    FormView.include({
        start: function() {
            var self = this;
            if(self.model == 'pos.booking' || self.dataset.model == 'pos.booking' || self.model == 'pos.booking.line'){
                $("#print_receipt_btn").remove();
                var $print_btn = "<button id='print_receipt_btn' class='btn btn-sm'>Print Receipt</button>";
                $(".o_form_view header").prepend($print_btn);
                $("#print_receipt_btn").on('click',function(){
                    self.print_pos_receipt()
                });
            }
            return this._super();
        },
        print: function(receipt,printer_ip){
            var self = this;
            if(printer_ip){
                self.connection = new Session(undefined,'http://' + printer_ip, { use_cors: true});
                framework.blockUI();
                self.connection.rpc('/hw_proxy/print_xml_receipt',{receipt: receipt},{timeout: 5000}).then(function(){
                    framework.unblockUI();
                },function(){framework.unblockUI();});
            }
        },
        print_pos_receipt : function(e){
            var self = this;
            var state = $.bbq.getState(true);
            framework.blockUI();
            var pos_order_model = new Model('pos.order');
            var pos_booking_model = new Model('pos.booking');
            pos_order_model.call("get_all_orders_data",[state.id]).then(function(res){
                framework.unblockUI();
                var vals = res[0].booking_number
                if (vals) {
                    var barcode_val = vals;
                    var barcode_src = false;
                    var barcodeTemplate = QWeb.render('barcodeTemplate',{
                          widget: self, barcode : barcode_val
                    });
                    $(barcodeTemplate).find("." + barcode_val.toString()).barcode(barcode_val.toString(), "code128");
                    if(_.isElement($(barcodeTemplate).find("." + barcode_val.toString()).barcode(barcode_val.toString(), "code128")[0])){
                        if($(barcodeTemplate).find("." + barcode_val.toString()).barcode(barcode_val.toString(), "code128")[0].firstChild != undefined 
                                && $(barcodeTemplate).find("." + barcode_val.toString()).barcode(barcode_val.toString(), "code128")[0].firstChild.data != undefined){
                            barcode_src = $(barcodeTemplate).find("." + barcode_val.toString()).barcode(barcode_val.toString(), "code128")[0].firstChild.data;
                        }
                    }
                    var pos_receipt = QWeb.render('Booking_Receipt',{receipt:res[0],widget:self,barcode_src:barcode_src});
                    self.print(pos_receipt, res[1]);
                }
            },function(){framework.unblockUI();});
        },
    })

});
