odoo.define('mis_pos_default_customer', function (require) {
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var ActionpadWidget = screens.ActionpadWidget;
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this,arguments);
            var self = this;
            if(this.pos.config.default_customer_id){
                client = this.pos.db.get_partner_by_id(self.pos.config.default_customer_id[0]);
                this.set_client(client);
            }
        },
    });
    ActionpadWidget.include({
        partner_icon_url: function(id){
            return '/web/image?model=res.partner&id='+id+'&field=image_small';
        },
    });
});