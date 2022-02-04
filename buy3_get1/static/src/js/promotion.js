"use strict";
odoo.define('buy3_get1.promotion', function (require) {
    var time = require('web.time');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var qweb = core.qweb;
    var gui = require('point_of_sale.gui');
    var PopupWidget = require('point_of_sale.popups');

    models.load_models([
        {
            model: 'pos.promotion',
            condition: function (self) {
                return self.config.promotion_ids && self.config.promotion_ids.length != 0;
            },
            fields: ['name', 'start_date', 'end_date', 'type', 'product_id'],
            domain: function (self) {
                return [
                    ['id', 'in', self.config.promotion_ids],
                    ['start_date', '<=', time.date_to_str(new Date()) + " " + time.time_to_str(new Date())],
                    ['end_date', '>=', time.date_to_str(new Date()) + " " + time.time_to_str(new Date())]
                ]
            },
            loaded: function (self, promotions) {
                self.promotions = promotions;
                self.promotion_by_id = {};
                self.promotion_ids = [];
                var i = 0;
                while (i < promotions.length) {
                    self.promotion_by_id[promotions[i].id] = promotions[i];
                    self.promotion_ids.push(promotions[i].id);
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.gift.condition',
            fields: ['product_id', 'minimum_quantity', 'promotion_id'],
            condition: function (self) {
                return self.promotion_ids && self.promotion_ids.length > 0;
            },
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            loaded: function (self, gift_conditions) {
                self.promotion_gift_condition_by_promotion_id = {};
                var i = 0;
                while (i < gift_conditions.length) {
                    if (!self.promotion_gift_condition_by_promotion_id[gift_conditions[i].promotion_id[0]]) {
                        self.promotion_gift_condition_by_promotion_id[gift_conditions[i].promotion_id[0]] = [gift_conditions[i]]
                    } else {
                        self.promotion_gift_condition_by_promotion_id[gift_conditions[i].promotion_id[0]].push(gift_conditions[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.gift.free',
            fields: ['product_id', 'quantity_free', 'promotion_id'],
            condition: function (self) {
                return self.promotion_ids && self.promotion_ids.length > 0;
            },
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            loaded: function (self, gifts_free) {
                self.promotion_gift_free_by_promotion_id = {};
                var i = 0;
                while (i < gifts_free.length) {
                    if (!self.promotion_gift_free_by_promotion_id[gifts_free[i].promotion_id[0]]) {
                        self.promotion_gift_free_by_promotion_id[gifts_free[i].promotion_id[0]] = [gifts_free[i]]
                    } else {
                        self.promotion_gift_free_by_promotion_id[gifts_free[i].promotion_id[0]].push(gifts_free[i])
                    }
                    i++;
                }
            }
        },

    ]);
    var _super_Orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        init_from_JSON: function (json) {
            var res = _super_Orderline.init_from_JSON.apply(this, arguments);
            if (json.promotion) {
                this.promotion = json.promotion;
            }
            if (json.promotion_reason) {
                this.promotion_reason = json.promotion_reason;
            }

            if (json.promotion_gift) {
                this.promotion_gift = json.promotion_gift;
            }

            return res;
        },
        export_as_JSON: function () {
            var json = _super_Orderline.export_as_JSON.apply(this, arguments);
            if (this.promotion) {
                json.promotion = this.promotion;
            }
            if (this.promotion_reason) {
                json.promotion_reason = this.promotion_reason;
            }

            if (this.promotion_gift) {
                json.promotion_gift = this.promotion_gift;
            }


            return json;
        },
        export_for_printing: function () {
            var receipt_line = _super_Orderline.export_for_printing.apply(this, arguments);
            receipt_line['promotion'] = null;
            receipt_line['promotion_reason'] = null;
            if (this.promotion) {
                receipt_line.promotion = this.promotion;
                receipt_line.promotion_reason = this.promotion_reason;
            }
            return receipt_line;
        },
        can_be_merged_with: function (orderline) {
            var merge = _super_Orderline.can_be_merged_with.apply(this, arguments);
            if (this.promotion) {
                return false;
            }
            return merge
        },
        set_quantity: function (quantity, keep_price) {
            _super_Orderline.set_quantity.apply(this, arguments);
            if (!this.promotion && quantity == 'remove' || quantity == '') {
                this.order.remove_all_promotion_line();
            }
        }
    });
    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super_Order.export_as_JSON.apply(this, arguments);
            if (this.promotion_amount) {
                json.promotion_amount = this.promotion_amount;
            }
            return json;
        },
        export_for_printing: function () {
            var receipt = _super_Order.export_for_printing.call(this);
            if (this.promotion_amount) {
                receipt.promotion_amount = this.promotion_amount;
            }
            return receipt
        },
//        validate_promotion: function () {
//            var self = this;
//            var datas = this.get_promotions_active();
//            var promotions_active = datas['promotions_active'];
//            if (promotions_active.length) {
//                this.pos.gui.show_screen('products');
//                this.pos.gui.show_popup('confirm', {
//                    title: 'Promotion active',
//                    body: 'Do you want to apply promotion on this order ?',
//                    confirm: function () {
//                        self.remove_all_promotion_line();
//                        self.compute_promotion();
//                        setTimeout(function () {
//                            self.validate_global_discount();
//                        }, 1000);
//                        self.pos.gui.show_screen('payment');
//                    },
//                    cancel: function () {
//                        setTimeout(function () {
//                            self.validate_global_discount();
//                        }, 1000);
//                        self.pos.gui.show_screen('payment');
//                    }
//                });
//            } else {
//                setTimeout(function () {
//                    self.validate_global_discount();
//                }, 1000);
//            }
//        },

        manual_compute_promotion: function (promotions) {
            this.remove_all_promotion_line();
            for (var i = 0; i < promotions.length; i++) {
                var type = promotions[i].type
                var order = this;
                if (order.orderlines.length) {


                    if (type == '5_pack_free_gift') {
                        order.compute_pack_free_gift(promotions[i]);
                    }

                }
            }
            var applied_promotion = false;
            for (var i = 0; i < this.orderlines.models.length; i++) {
                if (this.orderlines.models[i]['promotion'] == true) {
                    applied_promotion = true;
                    break;
                }
            }
            if (applied_promotion == false) {
                return this.pos.gui.show_popup('confirm', {
                    title: 'Warning',
                    body: 'Have not any promotion applied',
                });
            }
        },
        compute_promotion: function () {
            var promotions = this.pos.promotions;
            if (promotions) {
                this.remove_all_promotion_line();
                for (var i = 0; i < promotions.length; i++) {
                    var type = promotions[i].type
                    var order = this;
                    if (order.orderlines.length) {

                        if (type == '5_pack_free_gift') {
                            order.compute_pack_free_gift(promotions[i]);
                        }

                    }
                }
                var applied_promotion = false;
                for (var i = 0; i < this.orderlines.models.length; i++) {
                    if (this.orderlines.models[i]['promotion'] == true) {
                        applied_promotion = true;
                        break;
                    }
                }
                if (applied_promotion == false) {
                    return this.pos.gui.show_popup('confirm', {
                        title: 'Warning',
                        body: 'Have not any promotion applied',
                    });
                }
            }
        },

        remove_all_promotion_line: function () {
            var lines = this.orderlines.models;
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                if (line['promotion'] ||  line['promotion_gift'] ) {
                    this.remove_orderline(line);
                }
            }
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                if (line['promotion'] || line['promotion_gift'] ) {
                    this.remove_orderline(line);
                }
            }
        },
        product_quantity_by_product_id: function () {
            var lines_list = {};
            var lines = this.orderlines.models;
            var i = 0;
            while (i < lines.length) {
                var line = lines[i];
                if (line.promotion) {
                    i++;
                    continue
                }
                if (!lines_list[line.product.id]) {
                    lines_list[line.product.id] = line.quantity;
                } else {
                    lines_list[line.product.id] += line.quantity;
                }
                i++;
            }
            return lines_list
        },
        // 4 & 5 : check pack free gift and pack discount product
        checking_pack_discount_and_pack_free_gift: function (rules) {
            var can_apply = true;
            var product_quantity_by_product_id = this.product_quantity_by_product_id();
            for (var i = 0; i < rules.length; i++) {
                var rule = rules[i];
                var product_id = parseInt(rule.product_id[0]);
                var minimum_quantity = rule.minimum_quantity;
                if (!product_quantity_by_product_id[product_id] || product_quantity_by_product_id[product_id] < minimum_quantity) {
                    can_apply = false;
                }
            }
            return can_apply
        },
        count_quantity_by_product: function (product) {
            /*
                Function return total qty filter by product of order
            */
            var qty = 0;
            for (var i = 0; i < this.orderlines.models.length; i++) {
                var line = this.orderlines.models[i];
                if (line.product['id'] == product['id']) {
                    qty += line['quantity'];
                }
            }
            return qty;
        },
        compute_pack_free_gift: function (promotion) {
            /*
                5. Promotion free gift by pack products
            */
            var promotion_condition_items = this.pos.promotion_gift_condition_by_promotion_id[promotion.id];
            var check = this.checking_pack_discount_and_pack_free_gift(promotion_condition_items);
            if (check == true) {
                var gifts = this.pos.promotion_gift_free_by_promotion_id[promotion.id]
                if (!gifts) {
                    return;
                }
                var products_condition = {};
                for (var i = 0; i < promotion_condition_items.length; i++) {
                    var condition = promotion_condition_items[i];
                    var product = this.pos.db.get_product_by_id(condition.product_id[0]);
                    products_condition[product['id']] = this.count_quantity_by_product(product)
                }
                var can_continue = true;
                var temp = 1;
                for (var i = 1; i < 100; i++) {
                    for (var j = 0; j < promotion_condition_items.length; j++) {
                        var condition = promotion_condition_items[j];
                        var condition_qty = condition.minimum_quantity;
                        var product = this.pos.db.get_product_by_id(condition.product_id[0]);
                        var total_qty = this.count_quantity_by_product(product);
                        if (i * condition_qty <= total_qty) {
                            can_continue = true;
                        } else {
                            can_continue = false
                        }
                    }
                    if (can_continue == true) {
                        temp = i;
                    } else {
                        break;
                    }
                }
                var i = 0;
                while (i < gifts.length) {
                    var product = this.pos.db.get_product_by_id(gifts[i].product_id[0]);
                    if (product) {
                        this.add_promotion(product, 0, (gifts[i].quantity_free * temp), {
                            promotion: true,
                            promotion_gift: true,
                            promotion_reason: 'Applied  ' + promotion['name'] + ', give ' + (gifts[i].quantity_free * temp) + ' ' + product['display_name'],
                        })
                    }
                    i++;
                }
            }
        },

        add_promotion: function (product, price, quantity, options) {
            /*
                    Function apply promotions to current order
             */
            var line = new models.Orderline({}, {pos: this.pos, order: this.pos.get_order(), product: product});
            if (options.promotion) {
                line.promotion = options.promotion;
            }

            if (options.promotion_reason) {
                line.promotion_reason = options.promotion_reason;
            }

            if (options.promotion_gift) {
                line.promotion_gift = options.promotion_gift;
            }

            line.price_manually_set = true; // no need pricelist change, price of promotion change the same, i blocked
            line.set_quantity(quantity);
            line.set_unit_price(price);
            this.orderlines.add(line);
            this.trigger('change', this);
        },
        get_promotions_active: function () {
            var can_apply = null;
            var promotions_active = [];
            if (!this.pos.promotions) {
                return {
                    can_apply: can_apply,
                    promotions_active: []
                };
            }
            for (var i = 0; i < this.pos.promotions.length; i++) {
                var promotion = this.pos.promotions[i];
                if (promotion['type'] == '5_pack_free_gift') {
                    var promotion_condition_items = this.pos.promotion_gift_condition_by_promotion_id[promotion.id];
                    var checking_pack_discount_and_pack_free = this.checking_pack_discount_and_pack_free_gift(promotion_condition_items);
                    if (checking_pack_discount_and_pack_free) {
                        can_apply = checking_pack_discount_and_pack_free;
                        promotions_active.push(promotion);
                    }
                }

            }
            return {
                can_apply: can_apply,
                promotions_active: promotions_active
            };
        }
    });
    screens.OrderWidget.include({
        active_promotion: function (buttons, selected_order) {
            if (selected_order.orderlines && selected_order.orderlines.length > 0 && this.pos.config.promotion_ids.length > 0) {
                var lines = selected_order.orderlines.models;
                var promotion_amount = 0;
                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i]
                    if (line.promotion) {
                        promotion_amount += line.get_price_without_tax()
                    }
                }
                var promotion_datas = selected_order.get_promotions_active();
                var can_apply = promotion_datas['can_apply'];
                if (buttons && buttons.button_promotion) {
                    buttons.button_promotion.highlight(can_apply);
                }
//                var promotions_active = promotion_datas['promotions_active'];
//                if (promotions_active.length) {
//                    var promotion_recommend_customer_html = qweb.render('promotion_recommend_customer', {
//                        promotions: promotions_active
//                    });
//                    $('.promotion_recommend_customer').html(promotion_recommend_customer_html);
//                } else {
//                    $('.promotion_recommend_customer').html("");
//                }
            }
        },


        update_summary: function () {
            this._super();
            var selected_order = this.pos.get_order();
            var buttons = this.getParent().action_buttons;
            if (selected_order && buttons) {
                this.active_promotion(buttons, selected_order);


            }
        }
    });

    var button_promotion = screens.ActionButtonWidget.extend({// promotion button
        template: 'button_promotion',
        button_click: function () {
            var order = this.pos.get('selectedOrder');
            var promotion_manual_select = this.pos.config.promotion_manual_select;
            if (!promotion_manual_select) {
                order.compute_promotion()
            } else {
                var promotion_datas = order.get_promotions_active();
                var promotions_active = promotion_datas['promotions_active'];
                if (promotions_active.length) {
                    return this.pos.gui.show_popup('popup_selection_promotions', {
                        title: 'Promotions',
                        body: 'Please choice promotions and confirm',
                        promotions_active: promotions_active
                    })
                } else {
                    return this.pos.gui.show_popup('confirm', {
                        title: 'Warning',
                        body: 'Nothing promotions active',
                    })
                }

            }
        }
    });
    screens.define_action_button({
        'name': 'button_promotion',
        'widget': button_promotion,
        'condition': function () {
            return this.pos.promotion_ids && this.pos.promotion_ids.length >= 1;
        }
    });


    var popup_selection_promotions = PopupWidget.extend({ // add tags
        template: 'popup_selection_promotions',
        show: function (options) {
            var self = this;
            this._super(options);
            this.promotions_selected = {};
            var promotions = options.promotions_active;
            this.promotions = promotions;
            self.$el.find('.body').html(qweb.render('promotion_list', {
                promotions: promotions,
                widget: self
            }));
            this.$('.product').click(function () {
                var promotion_id = parseInt($(this).data('id'));
                var promotion = self.pos.promotion_by_id[promotion_id];
                if (promotion) {
                    if ($(this).closest('.product').hasClass("item-selected") == true) {
                        $(this).closest('.product').toggleClass("item-selected");
                        delete self.promotions_selected[promotion.id];
                    } else {
                        $(this).closest('.product').toggleClass("item-selected");
                        self.promotions_selected[promotion.id] = promotion;
                    }
                }
            });
            this.$('.cancel').click(function () {
                self.pos.gui.close_popup();
            });
            this.$('.confirm').click(function () {
                self.pos.gui.close_popup();
                var promotions = [];
                for (var i in self.promotions_selected) {
                    promotions.push(self.promotions_selected[i]);
                }
                if (promotions.length) {
                    self.pos.get_order().manual_compute_promotion(promotions)
                }
            });
            this.$('.add_all').click(function () {
                self.pos.get_order().manual_compute_promotion(self.promotions);
                self.pos.gui.close_popup();
            });
        }
    });
    gui.define_popup({name: 'popup_selection_promotions', widget: popup_selection_promotions});


});
