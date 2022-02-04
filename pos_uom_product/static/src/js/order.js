odoo.define('pos_uom_product.order', function (require) {

    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;
    var screens = require('point_of_sale.screens');


    var _super_Orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({


        init_from_JSON: function (json) {
            var res = _super_Orderline.init_from_JSON.apply(this, arguments);

            if (json.uom_id) {
                this.uom_id = json.uom_id;
                var unit = this.pos.units_by_id[json.uom_id];
                if (unit) {
                    this.product.uom_id = [unit['id'], unit['name']];
                }
            }
           return res;
     },
     export_as_JSON: function () {
            var json = _super_Orderline.export_as_JSON.apply(this, arguments);

            if (this.uom_id) {
                json.uom_id = this.uom_id;
            }
            return json;
     },

        get_unit: function () {
            if (!this.uom_id) {
                return _super_Orderline.get_unit.apply(this, arguments);
            } else {
                var unit_id = this.uom_id
                return this.pos.units_by_id[unit_id];
            }
        },
        is_multi_unit_of_measure: function () {
            var uom_items = this.pos.uoms_prices_by_product_tmpl_id[this.product.product_tmpl_id]
            if (!uom_items) {
                return false;
            }
            if (uom_items.length > 0) {
                return true;
            } else {
                return false;
            }
        },
    });


    screens.OrderWidget.include({
        update_summary: function(){
            this._super();
            var selected_order = this.pos.get_order();
            if (selected_order) {
                var buttons = this.getParent().action_buttons;
                if (selected_order && selected_order.selected_orderline) {
                    var is_multi_unit = selected_order.selected_orderline.is_multi_unit_of_measure();
                    if (buttons && buttons.button_choice_uom) {
                        buttons.button_choice_uom.highlight(is_multi_unit);
                    }
                }
                }

        }
    });




});
