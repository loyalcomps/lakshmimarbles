odoo.define('pos_keyboard_short.keyboard_shortcuts', function(require) {
    "use strict";
    var Model = require('web.Model');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var NumpadWidget = screens.NumpadWidget;
    var PaymentScreenWidget = screens.PaymentScreenWidget;
    var ReceiptScreenWidget = screens.ReceiptScreenWidget;
    var ClientListScreenWidget = screens.ClientListScreenWidget;
    var FormView = require('web.FormView');
    var gui = require('point_of_sale.gui');
    var resultarray;
    var core = require('web.core');


    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            this.keypad = new Keypad({'pos': this});
            return _super_posmodel.initialize.call(this, session, attributes);
        }
    });


    NumpadWidget.include({
        start: function() {
            this._super();
            var self = this;
            this.pos.keypad.set_action_callback(function(data){
                 self.keypad_action(data, self.pos.keypad.type);
            });
        },
        keypad_action: function(data, type){
             if (data.type === type.numchar){
                 this.state.appendNewChar(data.val);
             }
             else if (data.type === type.bmode) {
                 this.state.changeMode(data.val);
             }
             else if (data.type === type.sign){
                 this.clickSwitchSign();
             }
             else if (data.type === type.backspace){
                 this.clickDeleteLastChar();
             }
        }
    });

//    $(document).ready(function() {
//        (new Model('pos.shortcut')).call('paymentscreen', [
//            []
//        ]).then(function(result_dic) {
//            resultarray = result_dic;
//        });
//    });
    ClientListScreenWidget.include({
        show: function() {
            var self = this;
            this._super();
            this.pi_client_keyboard_handler = function(event) {
                if (event.type === "keydown") {
                    if (event.keyCode == 37) {
                        console.log("log2");
                        self.gui.back();
                    }
                    if (event.keyCode == 13) {
                        if ($(".next").is(":visible")) {
                            self.save_changes();
                            self.gui.back();
                        }
                    }
                }
            }
            window.document.body.addEventListener('keydown', this.pi_client_keyboard_handler);
        },
        hide: function() {
            window.document.body.removeEventListener('keydown', this.pi_client_keyboard_handler);
            this._super();
        },
    });
    PaymentScreenWidget.include({
        show: function() {
            var self = this;
            this._super();
            this.pos.keypad.disconnect();
            this.pi_client_keyboard_handler = function(event) {
                if (event.type === "keydown") {
                    if (event.keyCode == 37) {
                        self.click_back();
                        console.log("log1");
                    }
                }
            }
            this.pi_client_keyboard_handler_keypress = function(event) {
                if (event.type === "keypress") {
//                    if (resultarray.invoice) {
//                        if (event.keyCode == resultarray.invoice) {
//                            if ($(".js_invoice").hasClass("highlight")) {
//                                $('.js_invoice').removeClass('highlight');
//                            } else {
//                                $('.js_invoice').addClass('highlight');
//                            }
//                        }
//                    }

                       if (event.keyCode == 105) {
                           if ($(".js_invoice").hasClass("highlight")) {
                               $('.js_invoice').removeClass('highlight');
                           } else {
                               $('.js_invoice').addClass('highlight');
                           }
                       }

                }
            }
            window.document.body.addEventListener('keydown', this.pi_client_keyboard_handler);
            window.document.body.addEventListener('keypress', this.pi_client_keyboard_handler_keypress);
        },
        hide: function() {
            window.document.body.removeEventListener('keydown', this.pi_client_keyboard_handler);
            window.document.body.removeEventListener('keypress', this.pi_client_keyboard_handler_keypress);
            this._super();
            this.pos.keypad.connect();
        },
    });
    ReceiptScreenWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
            this.pi_keyboard_handler = function(event) {
                var key = '';
                if (event.type === "keydown") {
                    if (event.keyCode == 27 || event.keyCode == 13) {
                        if (!self._locked) {
                            self.click_next();
                        }
                    }
                    if (event.keyCode == 80) {
                        $(".button.print").trigger("click");
                    }
                }
            }
        },
        show: function() {
            window.document.body.addEventListener('keydown', this.pi_keyboard_handler);
            this._super();
        },
        hide: function() {
            window.document.body.removeEventListener('keydown', this.pi_keyboard_handler);
            this._super();
        },
        start: function() {
            $(document).keydown(function(e) {
                if ($(".product-screen").is(":visible")) {}
            });
            $(document).keypress(function(e) {
                var keyCode = e.keyCode;
                if (e.keyCode == 43) {
                    $(".neworder-button").trigger("click");
                }
                if (e.keyCode == 45) {
                    $(".deleteorder-button").trigger("click");
                }
                if (e.keyCode == 33) {
                    $(".order-button.select-order.selected").prev().trigger("click");
                }
                if (e.keyCode == 34) {
                    $(".order-button.select-order.selected").next().trigger("click");
                }
                if ($(".product-screen").is(":visible")) {
//                    if (e.keyCode >= 48 && e.keyCode <= 57) {
//                        var key = '' + (e.keyCode - 48);
//                        if (key == 1) {
//                            $(".pi_one").trigger("click");
//                        } else if (key == 2) {
//                            $(".pi_two").trigger("click");
//                        } else if (key == 3) {
//                            $(".pi_three").trigger("click");
//                        } else if (key == 4) {
//                            $(".pi_four").trigger("click");
//                        } else if (key == 5) {
//                            $(".pi_five").trigger("click");
//                        } else if (key == 6) {
//                            $(".pi_six").trigger("click");
//                        } else if (key == 7) {
//                            $(".pi_seven").trigger("click");
//                        } else if (key == 8) {
//                            $(".pi_eight").trigger("click");
//                        } else if (key == 9) {
//                            $(".pi_nine").trigger("click");
//                        } else if (key == 0) {
//                            $(".pi_zero").trigger("click");
//                        }
//                    }
//                    if (e.keyCode == 46) {
//                        $(".pi_dot").trigger("click");
//                    }
                    if (e.keyCode == 9) {
                        if ($("div.searchbox input").is(':not(:focus)')) {
                            setTimeout(function() {
                                $("div.searchbox input").focus();
                            });
                        } else if ($("div.searchbox input").is(":focus")) {
                            setTimeout(function() {
                                $(".leftpane").focus();
                            });
                            $(".orderlines li").first().addClass("selected");
                            $(".selected").trigger("click");
                        }
                    }
                    if ($("div.searchbox input").is(':not(:focus)')) {
//                        if (resultarray.payment) {
//                            if (e.keyCode == resultarray.payment) {
//                                $(".pay").trigger("click");
//                                $(".paymentmethods").focus();
//                            }
//                        }
//                        if (resultarray.total_discount) {
//                            if (e.keyCode == resultarray.total_discount) {
//                                if ($(".js_discount").is(":visible")) {
//                                    $(".js_discount").trigger("click");
//                                }
//                            }
//                        }
//                        if (resultarray.customer) {
//                            if (e.keyCode == resultarray.customer) {
//                                $(".set-customer").trigger("click");
//                                $(".searchbox input").focus();
//                            }
//                        }
//                        if (resultarray.price) {
//                            if (e.keyCode == resultarray.price) {
//                                $(".pi_price").trigger("click");
//                            }
//                        }
//                        if (resultarray.qty) {
//                            if (e.keyCode == resultarray.qty) {
//                                $(".pi_qty").trigger("click");
//                            }
//                        }
//                        if (resultarray.disc) {
//                            if (e.keyCode == resultarray.disc) {
//                                $(".pi_disc").trigger("click");
//                            }
//                        }



//                           if (e.keyCode == 112) {
//                               $(".pay").trigger("click");
//                               $(".paymentmethods").focus();
//                           }


                           if (e.keyCode == 116) {
                               if ($(".js_discount").is(":visible")) {
                                   $(".js_discount").trigger("click");
                               }
                           }


                           if (e.keyCode == 99) {
                               $(".set-customer").trigger("click");
                               $(".searchbox input").focus();
                           }
//
//
//                           if (e.keyCode == 114) {
//                              $(".pi_price").trigger("click");
//                           }
//
//
//                           if (e.keyCode == 113) {
//                               $(".pi_qty").trigger("click");
//                           }
//
//
//                           if (e.keyCode == 100) {
//                               $(".pi_disc").trigger("click");
//                           }


                    }
                } else if ($(".clientlist-screen").is(":visible")) {
//                    if (e.keyCode == resultarray.customer) {
//                        if (e.keyCode == resultarray.customer) {
//                            $(".new-customer").trigger("click");
//                        }
//                    }
                        if (e.keyCode == 115) {
                        if (e.keyCode == 115) {
                            $(".new-customer").trigger("click");
                        }
                    }
                } else if ($(".payment-screen").is(":visible")) {
                    if (!$(".paymentline").hasClass("selected")) {
                        if (e.keyCode >= 48 && e.keyCode <= 57) {
                            var payment_key = '' + (e.keyCode - 48);
                            if (e.keyCode == e.keyCode) {
                                payment_key = payment_key - 1;
                                $(".paymentmethods").children().eq(payment_key).trigger('click');
                            }
                        }
                    }
                    if (e.keyCode == 100) {
                        $("tr.paymentline.selected").find("td.delete-button").trigger("click");
                    }
//                    if (resultarray.customer) {
//                        if (e.keyCode == resultarray.customer) {
//                            $(".js_set_customer").trigger("click");
//                            $(".searchbox input").focus();
//                        }
//                    }

                        if (e.keyCode == 115) {
                            $(".js_set_customer").trigger("click");
                            $(".searchbox input").focus();
                        }

                }
            });
            $(document).keydown(function(e) {
                if ($(".product-screen").is(":visible")) {
                    if (e.keyCode == 9) {
                        if ($("div.searchbox input").is(':not(:focus)')) {
                            setTimeout(function() {
                                $("div.searchbox input").focus();
                            });
                        } else if ($("div.searchbox input").is(":focus")) {
                            setTimeout(function() {
                                $(".leftpane").focus();
                            });
                            $(".orderlines li").first().addClass("selected");
                            $(".selected").trigger("click");
                        }
                    }
                    if ($("div.searchbox input").is(':not(:focus)')) {
                        if (e.keyCode == 8) {
                            $(".pi_numpad_backspace").trigger("click");
                        }
                        if (e.keyCode == 39) {
                            if ($("div.searchbox input").is(':not(:focus)')) {
                                $(".pay").trigger("click");
                                $(".paymentmethods").focus();
                            }
                        }
                        if (e.keyCode == 38) {
                            if ($('li.selected').is(':not(:first-child)')) {
                                var cur_li = $("li.selected");
                                var pre_li = $("li.selected").prev();
                                if (pre_li) {
                                    cur_li.removeClass('selected');
                                    pre_li.addClass('selected');
                                    $(".selected").trigger("click");
                                }
                            }
                            var selectedElement = $(".orderline.selected");
                            if (selectedElement.position()){
                                var currentPositionY = selectedElement.position().top;
                            }
                            else{
                                return
                            }

                            var elementIndex = selectedElement.index();
                            var elementHeight = 55;
                            var scrollTo = elementIndex * 55;
                            $(".order-scroller").scrollTop(scrollTo);
                        } else if (e.keyCode == 40) {
                            if ($('li.selected').is(':not(:last-child)')) {
                                var cur_li = $("li.selected");
                                var next_li = $("li.selected").next();
                                cur_li.removeClass('selected');
                                next_li.addClass('selected');
                                $(".selected").trigger("click");
                            }
                            var selectedElement = $(".orderline.selected");
                            if (selectedElement.position()){
                                var currentPositionY = selectedElement.position().top;
                            }
                            else{
                                return
                            }
                            var currentPositionY = selectedElement.position().top;
                            var elementIndex = selectedElement.index();
                            var leftPaneHeight = $(".order-scroller").height();
                            var elementHeight = 55;
                            var scrollTo = elementIndex * 55;
                            $(".order-scroller").scrollTop(scrollTo);
                        }
                    }
                }
            });
        }
    });
//    NumpadWidget.include({
//        start: function() {
//            this.state.bind('change:mode', this.changedMode, this);
//            this.changedMode();
//            this.$el.find('.numpad-minus').click(_.bind(this.clickSwitchSign, this));
//            this.$el.find('.mode-button').click(_.bind(this.clickChangeMode, this));
//            this.$el.find('.pi_one').click(_.bind(this.clickAppendNewChar, this));
//            this.$el.find('.pi_two').click(_.bind(this.clickAppendNewChar, this));
//            this.$el.find('.pi_three').click(_.bind(this.clickAppendNewChar, this));
//            this.$el.find('.pi_four').click(_.bind(this.clickAppendNewChar, this));
//            this.$el.find('.pi_five').click(_.bind(this.clickAppendNewChar, this));
//            this.$el.find('.pi_six').click(_.bind(this.clickAppendNewChar, this));
//            this.$el.find('.pi_seven').click(_.bind(this.clickAppendNewChar, this));
//            this.$el.find('.pi_eight').click(_.bind(this.clickAppendNewChar, this));
//            this.$el.find('.pi_nine').click(_.bind(this.clickAppendNewChar, this));
//            this.$el.find('.pi_zero').click(_.bind(this.clickAppendNewChar, this));
//            this.$el.find('.pi_dot').click(_.bind(this.clickAppendNewChar, this));
//            this.$el.find('.pi_numpad_backspace').click(_.bind(this.clickDeleteLastChar, this));
//            this.$el.find('.pi_price').click(_.bind(this.clickChangeMode, this));
//            this.$el.find('.pi_disc').click(_.bind(this.clickChangeMode, this));
//            this.$el.find('.pi_qty').click(_.bind(this.clickChangeMode, this));
//        }
//    });

    var Keypad = core.Class.extend({
        init: function(attributes){
            this.pos = attributes.pos;
            /*this.pos_widget = this.pos.pos_widget;*/
            this.type = {
                numchar: 'number, dot',
                bmode: 'quantity, discount, price',
                sign: '+, -',
                backspace: 'backspace'
            };
            this.data = {
                type: undefined,
                val: undefined
            };
            this.action_callback = undefined;
        },

        save_callback: function(){
            this.saved_callback_stack.push(this.action_callback);
        },

        restore_callback: function(){
            if (this.saved_callback_stack.length > 0) {
                this.action_callback = this.saved_callback_stack.pop();
            }
        },

        set_action_callback: function(callback){
            this.action_callback = callback;
        },

        //remove action callback
        reset_action_callback: function(){
            this.action_callback = undefined;
        },

        // starts catching keyboard events and tries to interpret keystrokes,
        // calling the callback when needed.
        connect: function(){
            var self = this;
            // --- additional keyboard ---//
            var KC_PLU = 107;      // KeyCode: + or - (Keypad '+')
            var KC_QTY = 111;      // KeyCode: Quantity (Keypad '/')
            var KC_AMT = 106;      // KeyCode: Price (Keypad '*')
            var KC_DISC = 109;     // KeyCode: Discount Percentage [0..100] (Keypad '-')
            // --- basic keyboard --- //
            var KC_PLU_1 = 83;    // KeyCode: sign + or - (Keypad 's')
            var KC_QTY_1 = 81;     // KeyCode: Quantity (Keypad 'q')
            var KC_AMT_1 = 80;     // KeyCode: Price (Keypad 'p')
            var KC_DISC_1 = 68;    // KeyCode: Discount Percentage [0..100] (Keypad 'd')

            var KC_BACKSPACE = 8;  // KeyCode: Backspace (Keypad 'backspace')
            var kc_lookup = {
                48: '0', 49: '1', 50: '2',  51: '3', 52: '4',
                53: '5', 54: '6', 55: '7', 56: '8', 57: '9',
                80: 'p', 83: 's', 68: 'd', 190: '.', 81: 'q',
                96: '0', 97: '1', 98: '2',  99: '3', 100: '4',
                101: '5', 102: '6', 103: '7', 104: '8', 105: '9',
                106: '*', 107: '+', 109: '-', 110: '.', 111: '/'
            };

            //usb keyboard keyup event
            var rx = /INPUT|SELECT|TEXTAREA/i;
            var ok = false;
            var timeStamp = 0;
            $('body').on('keyup', '', function (e){
                var statusHandler  =  !rx.test(e.target.tagName)  ||
                    e.target.disabled || e.target.readOnly;
                if (statusHandler){
                    var is_number = false;
                    var type = self.type;
                    var buttonMode = {
                        qty: 'quantity',
                        disc: 'discount',
                        price: 'price'
                    };
                    var token = e.keyCode;
                    if ((token >= 96 && token <= 105 || token == 110) ||
                        (token >= 48 && token <= 57 || token == 190)) {
                        self.data.type = type.numchar;
                        self.data.val = kc_lookup[token];
                        is_number = true;
                        ok = true;
                    }
                    else if (token == KC_PLU || token == KC_PLU_1) {
                        self.data.type = type.sign;
                        ok = true;
                    }
                    else if (token == KC_QTY || token == KC_QTY_1) {
                        self.data.type = type.bmode;
                        self.data.val = buttonMode.qty;
                        ok = true;
                    }
                    else if (token == KC_AMT || token == KC_AMT_1) {
                        self.data.type = type.bmode;
                        self.data.val = buttonMode.price;
                        ok = true;
                    }
                    else if (token == KC_DISC || token == KC_DISC_1) {
                        self.data.type = type.bmode;
                        self.data.val = buttonMode.disc;
                        ok = true;
                    }
                    else if (token == KC_BACKSPACE) {
                        self.data.type = type.backspace;
                        ok = true;
                    }
                    else {
                        self.data.type = undefined;
                        self.data.val = undefined;
                        ok = false;
                    }

                    if (is_number) {
                        if (timeStamp + 50 > new Date().getTime()) {
                            ok = false;
                        }
                    }

                    timeStamp = new Date().getTime();

                    setTimeout(function(){
                        if (ok) {self.action_callback(self.data);}
                    }, 50);
                }
            });
        },

        // stops catching keyboard events
        disconnect: function(){
            $('body').off('keyup', '');
        }
    });

    return {
        Keypad: Keypad
    };
});