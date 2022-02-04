odoo.define("pos_receipt.arabic",function (require) {


//my code******************************************************************N E W  C O D E****************************************************************************************

    var models = require('point_of_sale.models');
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function(model){ return model.model === 'product.product'; });
            partner_model.fields.push('arabic_name');
            var partner_model = _.find(this.models, function(model){ return model.model === 'res.company'; });
            partner_model.fields.push('arabic_name');
            var partner_model = _.find(this.models, function(model){ return model.model === 'res.company'; });
            partner_model.fields.push('logo');
            return _super_posmodel.initialize.call(this, session, attributes);
        },
    });

//    models.PosModel = models.PosModel.extend({
//        initialize: function (session, attributes) {
//
//            return _super_posmodel.initialize.call(this, session, attributes);
//        },
//    });


//*******************************************************************************************************************************************************************************

});
