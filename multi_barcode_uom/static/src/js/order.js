odoo.define('multi_barcode_uom.order', function (require) {

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

    });




});
