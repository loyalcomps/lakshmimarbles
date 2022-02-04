odoo.define('pos_combopack.combo', function (require) {
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var _t = core._t;
    var gui = require('point_of_sale.gui');
    var PopupWidget = require('point_of_sale.popups');
    var QWeb = core.qweb;


     var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var product_model = _.find(this.models, function (model) {
                return model.model === 'product.product';
            });
            product_model.fields.push('combo_limit');
            return _super_posmodel.initialize.apply(this, arguments);
        },
    });

    models.load_models([
        {
            model: 'pos.combo.pack',
            fields: ['product_id', 'product_combo_id', 'default', 'quantity'],
            loaded: function (self, combo_items) {
                self.combo_items = combo_items;
                self.combo_by_id = {}
                for (var i = 0; i < combo_items.length; i++) {
                    self.combo_by_id[combo_items[i].id] = combo_items[i];
                }
            }
        }
    ]);

    var ComboItems = PopupWidget.extend({
        template: 'ComboItems',
        show: function (options) {
            var self = this;
            this._super(options);
            var combo_items = options.combo_items;
            var selected_orderline = options.selected_orderline;
            var combo_items_selected = selected_orderline['combo_items'];
            if (combo_items_selected.length != 0) {
                for (var i = 0; i < combo_items.length; i++) {
                    var combo_item = _.findWhere(combo_items_selected, {id: combo_items[i].id});
                    if (combo_item) {
                        combo_items[i]['selected'] = true
                    } else {
                        combo_items[i]['selected'] = false
                    }
                }
            }
            self.combo_item_of_line = selected_orderline['combo_items'];
            var image_url = window.location.origin + '/web/image?model=product.product&field=image_medium&id=';
            self.$el.find('div.body').html(QWeb.render('ComboItem', {
                combo_items: combo_items,
                image_url: image_url,
                widget: self
            }));

            $('.combo-item').click(function () {
                var combo_item_id = parseInt($(this).data('id'));
                var combo_item = self.pos.combo_by_id[combo_item_id];
                if (!self.pos.get_order().selected_orderline) {
                    return;
                }
                if (combo_item) {
                    if ($(this).closest('.product').hasClass("item-selected") == true) {
                        $(this).closest('.product').toggleClass("item-selected");
                        for (var i = 0; i < self.combo_item_of_line.length; ++i) {
                            if (self.combo_item_of_line[i].id == combo_item.id) {
                                self.combo_item_of_line.splice(i, 1);
                                selected_orderline.trigger('change', selected_orderline)
                                selected_orderline.trigger('update:OrderLine');
                            }
                        }
                    } else {
                        if (self.pos.get_order().selected_orderline['combo_items'].length >= self.pos.get_order().selected_orderline.product.combo_limit) {
                            self.gui.show_popup('error', {
                                'title': _t('Error'),
                                'body': _t('Combo: ' + selected_orderline.product.display_name + ' have limit item ' + selected_orderline.product.combo_limit)
                            });
                            return;
                        } else {
                            $(this).closest('.product').toggleClass("item-selected");
                            self.combo_item_of_line.push(combo_item);
                            selected_orderline.trigger('change', selected_orderline)
                            selected_orderline.trigger('update:OrderLine');
                        }
                    }

                }
                var order = self.pos.get('selectedOrder');
                order.trigger('change', order)
            });
        }
    });
    gui.define_popup({name: 'ComboItems', widget: ComboItems});


    var ComboButton = screens.ActionButtonWidget.extend({
        template: 'ComboButton',
        init: function (parent, options) {
            this._super(parent, options);

            this.pos.get('orders').bind('add remove change', function () {
                this.renderElement();
            }, this);

            this.pos.bind('change:selectedOrder', function () {
                this.renderElement();
            }, this);
        },
        button_click: function () {
            var selected_orderline = this.pos.get_order().selected_orderline;
            if (!selected_orderline) {
                return;
            }
            var combo_items = [];
            for (var i = 0; i < this.pos.combo_items.length; i++) {
                var combo_item = this.pos.combo_items[i];
                if (combo_item.product_combo_id[0] == selected_orderline.product.product_tmpl_id) {
                    combo_items.push(combo_item);
                }
            }
            if (!selected_orderline) {
                this.gui.show_popup('error', {
                    'title': _t('Error'),
                    'body': _t('Please selected line before change a combo items')
                });
                return;
            } else {
                if (combo_items.length) {
                    this.gui.show_popup('ComboItems', {
                        combo_items: combo_items,
                        selected_orderline: selected_orderline,
                    });
                } else {
                    this.gui.show_popup('error', {
                        'title': _t('Error'),
                        'body': _t('Line selected is not product combo')
                    });
                    return;
                }

            }


        },
    });

    screens.define_action_button({
        'name': 'combo_button',
        'widget': ComboButton,
        'condition': function () {
            return true;
        },
    });
    var _super_order_line = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attributes, options) {
            _super_order_line.initialize.apply(this, arguments);
            if (!this.combo_items) {
                this.combo_items = [];
            }
        },
        init_from_JSON: function (json) {
            _super_order_line.init_from_JSON.apply(this, arguments);
            if (json.combo_items) {
                this.combo_items = json.combo_items
            }
        },
        export_as_JSON: function () {
            var json = _super_order_line.export_as_JSON.apply(this, arguments);
            if (this.combo_items) {
                json.combo_items = this.combo_items;
            }
            return json
        },
        export_for_printing: function () {
            var datas = _super_order_line.export_for_printing.apply(this, arguments);
            if (this.combo_items) {
                datas['combo_items'] = this.combo_items;
            }
            return datas;
        },
        get_note: function (note) {
            var note = _super_order_line.get_note.apply(this, arguments);
            combo_notes = '';
            if (this.combo_items) {
                for (var i = 0; i < this.combo_items.length; i++) {
                    if (!variant_note) {
                        combo_notes += this.combo_items[i].product_id[1] + ' qty: ' + this.quantity;
                    } else {
                        combo_notes += ', ' + this.combo_items[i].product_id[1] + ' qty: ' + this.quantity;
                    }
                }
            }
            note += variant_note;
            return note;
        },
        is_combo: function () {
            var combo_items = [];
            for (var i = 0; i < this.pos.combo_items.length; i++) {
                var combo_item = this.pos.combo_items[i];
                if (combo_item.product_combo_id[0] == this.product['product_tmpl_id']) {
                    combo_items.push(combo_item);
                }
            }
            if (combo_items.length > 0) {
                return true
            } else {
                return false;
            }
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function (product, options) {
            var res = _super_order.add_product.apply(this, arguments);
            var selected_orderline = this.selected_orderline;
            var combo_items = [];
            for (var i = 0; i < this.pos.combo_items.length; i++) {
                var combo_item = this.pos.combo_items[i];
                if (combo_item.product_combo_id[0] == selected_orderline.product.product_tmpl_id && combo_item.default == true) {
                    combo_items.push(combo_item);
                }
            }
            selected_orderline['combo_items'] = combo_items;
            selected_orderline.trigger('change', selected_orderline);
            return res
        }
    });

    screens.OrderWidget.include({
    update_summary: function(){
        this._super();
        var selected_order = this.pos.get_order();
            if (selected_order) {

        var buttons = this.getParent().action_buttons;

        if (selected_order.selected_orderline && buttons && buttons.combo_button) {
            var is_combo = selected_order.selected_orderline.is_combo();
//            var has_combo_item_tracking_lot = selected_order.selected_orderline.has_combo_item_tracking_lot();
            buttons.combo_button.highlight(is_combo);
        }
        }
    },
});





//    var _super_posmodel = models.PosModel.prototype;
//    models.PosModel = models.PosModel.extend({
//        initialize: function (session, attributes) {
//            var product_model = _.find(this.models, function (model) {
//                return model.model === 'product.product';
//            });
//            product_model.fields.push('combo_limit');
//            return _super_posmodel.initialize.apply(this, arguments);
//        },
//    });
//
//    models.load_models([
//        {
//            model: 'pos.combo.pack',
//            fields: ['product_id', 'product_combo_id', 'default', 'quantity', 'uom_id', 'tracking'],
//            loaded: function (self, combo_items) {
//                self.combo_items = combo_items;
//                self.combo_item_by_id = {}
//                for (var i = 0; i < combo_items.length; i++) {
//                    self.combo_item_by_id[combo_items[i].id] = combo_items[i];
//                }
//            }
//        }
//    ]);
//
//
//    var button_combo = screens.ActionButtonWidget.extend({
//        template: 'button_combo',
//
//        button_click: function () {
//            var self = this;
//            var selected_orderline = this.pos.get_order().selected_orderline;
//            if (!selected_orderline) {
//                return;
//            }
//            var combo_items = [];
//            for (var i = 0; i < this.pos.combo_items.length; i++) {
//                var combo_item = this.pos.combo_items[i];
//                if (combo_item.product_combo_id[0] == selected_orderline.product.product_tmpl_id) {
//                    combo_items.push(combo_item);
//                }
//            }
//            if (!selected_orderline) {
//                return this.gui.show_popup('alert_result', {
//                    title: 'Warning',
//                    body: 'Please select line',
//                    confirm: function () {
//                        return self.gui.close_popup();
//                    }
//                });
//            } else {
//                if (combo_items.length) {
//                    this.gui.show_popup('popup_selection_combos', {
//                        title: 'Please choice items',
//                        combo_items: combo_items,
//                        selected_orderline: selected_orderline
//                    });
//                } else {
//                    return this.gui.show_popup('alert_result', {
//                        title: 'Warning',
//                        body: 'Line selected is not product pack/combo',
//                        confirm: function () {
//                            return self.gui.close_popup();
//                        }
//                    });
//                }
//            }
//        }
//    });
//
//    screens.define_action_button({
//        'name': 'button_combo',
//        'widget': button_combo,
//        'condition': function () {
//            return true;
//        }
//    });
//
//
//
//    var _super_order_line = models.Orderline.prototype;
//    models.Orderline = models.Orderline.extend({
//        initialize: function (attributes, options) {
//            _super_order_line.initialize.apply(this, arguments);
//            if (!this.combo_items) {
//                this.combo_items = [];
//            }
//        },
//        init_from_JSON: function (json) {
//            _super_order_line.init_from_JSON.apply(this, arguments);
//            if (json.combo_items) {
//                this.combo_items = json.combo_items
//            }
//        },
//        export_as_JSON: function () {
//            var json = _super_order_line.export_as_JSON.apply(this, arguments);
//            if (this.combo_items) {
//                json.combo_items = this.combo_items;
//            }
//            return json
//        },
//        export_for_printing: function () {
//            var datas = _super_order_line.export_for_printing.apply(this, arguments);
//            if (this.combo_items) {
//                datas['combo_items'] = this.combo_items;
//            }
//            return datas;
//        },
//        get_note: function (note) {
//            var note = _super_order_line.get_note.apply(this, arguments);
//            combo_notes = '';
//            if (this.combo_items) {
//                for (var i = 0; i < this.combo_items.length; i++) {
//                    if (!variant_note) {
//                        combo_notes += this.combo_items[i].product_id[1] + ' qty: ' + this.quantity;
//                    } else {
//                        combo_notes += ', ' + this.combo_items[i].product_id[1] + ' qty: ' + this.quantity;
//                    }
//                }
//            }
//            note += variant_note;
//            return note;
//        },
//    });
//
//    var _super_order = models.Order.prototype;
//    models.Order = models.Order.extend({
//        add_product: function (product, options) {
//            var res = _super_order.add_product.apply(this, arguments);
//            var selected_orderline = this.selected_orderline;
//            var combo_items = [];
//            for (var i = 0; i < this.pos.combo_items.length; i++) {
//                var combo_item = this.pos.combo_items[i];
//                if (combo_item.product_combo_id[0] == selected_orderline.product.product_tmpl_id && combo_item.default == true) {
//                    combo_items.push(combo_item);
//                }
//            }
//            selected_orderline['combo_items'] = combo_items;
//            selected_orderline.trigger('change', selected_orderline);
//            return res
//        }
//    });


});
