 odoo.define("pos_greeting_message.pos", function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var screens = require('point_of_sale.screens');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var popups = require("point_of_sale.popups");
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var PosDB = require("point_of_sale.DB");
    var PosBaseWidget = require('point_of_sale.BaseWidget');

    var utils = require('web.utils');

    var QWeb = core.qweb;

    var models = require('point_of_sale.models');
    var _super_posmodel = models.PosModel.prototype;
//    models.PosModel = models.PosModel.extend({
//        initialize: function (self,) {
//            var greeting_model = _.find(this.models, function(model){ return model.model === 'pos.config'; });
//            greeting_model.fields.push('greetings_active_char');
//
//
//
//            return _super_posmodel.initialize.call(this, session, attributes);
//        },
//    });


     });

