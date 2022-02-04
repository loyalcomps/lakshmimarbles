odoo.define('pos_combopack.popups', function (require) {

    var core = require('web.core');
    var _t = core._t;
    var gui = require('point_of_sale.gui');
    var PopupWidget = require('point_of_sale.popups');
    var qweb = core.qweb;


//    // select combo
//    var popup_selection_combos = PopupWidget.extend({
//        template: 'popup_selection_combos',
//        show: function (options) {
//            var self = this;
//            this._super(options);
//            var combo_items = options.combo_items;
//            var selected_orderline = options.selected_orderline;
//            var combo_items_selected = selected_orderline['combo_items'];
//            if (combo_items_selected.length != 0) {
//                for (var i = 0; i < combo_items.length; i++) {
//                    var combo_item = _.findWhere(combo_items_selected, {id: combo_items[i].id});
//                    if (combo_item) {
//                        combo_items[i]['selected'] = true
//                    } else {
//                        combo_items[i]['selected'] = false
//                    }
//                }
//            }
//            self.combo_item_of_line = selected_orderline['combo_items'];
//            var image_url = window.location.origin + '/web/image?model=product.product&field=image_medium&id=';
//            self.$el.find('div.body').html(qweb.render('combo_items', {
//                combo_items: combo_items,
//                image_url: image_url,
//                widget: self
//            }));
//
//            $('.combo-item').click(function () {
//                var combo_item_id = parseInt($(this).data('id'));
//                var combo_item = self.pos.combo_item_by_id[combo_item_id];
//                if (!self.pos.get_order().selected_orderline) {
//                    return;
//                }
//                if (combo_item) {
//                    if ($(this).closest('.product').hasClass("item-selected") == true) {
//                        $(this).closest('.product').toggleClass("item-selected");
//                        for (var i = 0; i < self.combo_item_of_line.length; ++i) {
//                            if (self.combo_item_of_line[i].id == combo_item.id) {
//                                self.combo_item_of_line.splice(i, 1);
//                                selected_orderline.trigger('change', selected_orderline)
//                                selected_orderline.trigger('update:OrderLine');
//                            }
//                        }
//                    } else {
//                        if (self.pos.get_order().selected_orderline['combo_items'].length >= self.pos.get_order().selected_orderline.product.combo_limit) {
//                            return self.gui.show_popup('alert_result', {
//                                title: 'Warning',
//                                body: 'You can not add bigger than ' + selected_orderline.product.combo_limit + ' items'
//                            });
//                        } else {
//                            $(this).closest('.product').toggleClass("item-selected");
//                            self.combo_item_of_line.push(combo_item);
//                            selected_orderline.trigger('change', selected_orderline)
//                            selected_orderline.trigger('update:OrderLine');
//                        }
//                    }
//
//                }
//                var order = self.pos.get('selectedOrder');
//                order.trigger('change', order)
//            });
//            $('.cancel').click(function () {
//                self.gui.close_popup();
//            });
//        }
//    });
//    gui.define_popup({name: 'popup_selection_combos', widget: popup_selection_combos});

    // add lot to combo items
//    var popup_add_lot_to_combo_items = PopupWidget.extend({
//        template: 'popup_add_lot_to_combo_items',
//        events: _.extend({}, PopupWidget.prototype.events, {
//            'click .remove-lot': 'remove_lot',
//            'blur .packlot-line-input': 'lose_input_focus'
//        }),
//
//        show: function (options) {
//            this.orderline = options.orderline;
//            this.combo_items = options.combo_items;
//            this._super(options);
//            this.focus();
//        },
//        lose_input_focus: function (ev) {
//            var $input = $(ev.target),
//                id = $input.attr('id');
//            var combo_item = this.pos.combo_item_by_id[id];
//            var lot = this.pos.lot_by_name[$input.val()];
//            if (lot) {
//                combo_item['use_date'] = lot['use_date']
//            } else {
//                combo_item['lot_number'] = 'Wrong lot, input again.';
//            }
//            for (var i = 0; i < this.orderline.combo_items.length; i++) {
//                if (this.orderline.combo_items[i]['id'] == id) {
//                    this.orderline.combo_items[i] = combo_item;
//                }
//            }
//            this.orderline.trigger('change', this.orderline);
//        },
//        remove_lot: function (ev) {
//            $input = $(ev.target).prev(),
//                id = $input.attr('id');
//            var combo_item = this.pos.combo_item_by_id[id];
//            combo_item['lot_number'] = '';
//            combo_item['use_date'] = '';
//            for (var i = 0; i < this.orderline.combo_items.length; i++) {
//                if (this.orderline.combo_items[i]['id'] == id) {
//                    this.orderline.combo_items[i] = combo_item;
//                }
//            }
//            this.orderline.trigger('change', this.orderline);
//            this.renderElement();
//        },
//
//        focus: function () {
//            this.$("input[autofocus]").focus();
//            this.focus_model = false;   // after focus clear focus_model on widget
//        }
//    });
//    gui.define_popup({name: 'popup_add_lot_to_combo_items', widget: popup_add_lot_to_combo_items});

});
