odoo.define('pos_uom_product.buttons', function (require) {

    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var _t = core._t;
    var rpc = require('web.rpc');
    var qweb = core.qweb;


    var button_choice_uom = screens.ActionButtonWidget.extend({
        template: 'button_choice_uom',
        button_click: function () {
            var self = this;
            var order = this.pos.get_order()
            if (order) {
                var selected_orderline = order.selected_orderline;
                if (selected_orderline) {
                    var product = selected_orderline.product;
                    var uom_items = this.pos.uoms_prices_by_product_tmpl_id[product.product_tmpl_id]
                    if (!uom_items) {

                          this.gui.show_popup('error', {
                           'title': _t('Error'),
//                           'body': _t('Please select line')
                             'body': product['display_name'] + ' has  ' + product['uom_id'][1] + ' only.',
                          });
                          return;

//                        this.gui.show_popup('notify_popup', {
//                            title: 'ERROR',
//                            from: 'top',
//                            align: 'center',
//                            body: product['display_name'] + ' have ' + product['uom_id'][1] + ' only.',
//                            color: 'danger',
//                            timer: 1000
//                        });
//                        return;
                    }
                    var list = [];
                    for (var i = 0; i < uom_items.length; i++) {
                        var item = uom_items[i];
                        list.push({
                            'label': item.uom_id[1],
                            'item': item,
                        });
                    }
                    if (list.length) {
                        this.gui.show_popup('selection', {
                            title: _t('Select Unit of measure'),
                            list: list,
                            confirm: function (item) {
                                selected_orderline.set_unit_price(item['price'])
                                selected_orderline.uom_id = item['uom_id'][0];
                                selected_orderline.trigger('change', selected_orderline);
                                selected_orderline.trigger('update:OrderLine');
                            }
                        });
                    } else {


                            this.gui.show_popup('error', {
                              'title': _t('Error'),
//                             'body': _t('Please select line')
                              'body': product['display_name'] + ' only one ' + product['uom_id'][1],
                            });
                            return;
//                        return this.gui.show_popup('alert_result', {
//                            title: 'Warning',
//                            body: product['display_name'] + ' only one ' + product['uom_id'][1],
//                            timer: 2000,
//                            confirm: function () {
//                                return self.gui.close_popup();
//                            },
//                            cancel: function () {
//                                return self.gui.close_popup();
//                            }
//                        });
                    }
                } else {


                      this.gui.show_popup('error', {
                      'title': _t('Error'),
                      'body': _t('Please select line')
                       });
                      return;


//                    return this.gui.show_popup('alert_result', {
//                        title: 'Warning',
//                        body: 'Please select line',
//                        confirm: function () {
//                            return self.gui.close_popup();
//                        },
//                        cancel: function () {
//                            return self.gui.close_popup();
//                        }
//                    });
                }
            } else {

                       this.gui.show_popup('error', {
                       'title': _t('Error'),
                       'body': _t('Order line is empty ')
                        });
                       return;


//                return this.gui.show_popup('alert_result', {
//                    title: 'Warning',
//                    body: 'Order Lines is empty',
//                    timer: 2000,
//                    confirm: function () {
//                        return self.gui.close_popup();
//                    },
//                    cancel: function () {
//                        return self.gui.close_popup();
//                    }
//                });
            }
        }
    });
    screens.define_action_button({
        'name': 'button_choice_uom',
        'widget': button_choice_uom,
        'condition': function () {
            return this.pos.uoms_prices.length && this.pos.uoms_prices.length > 0;
        }
    });


});