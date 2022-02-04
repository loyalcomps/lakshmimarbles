odoo.define('pos_auto_phone.PosPhone', function(require){
    "use strict";
    var screens = require('point_of_sale.screens');

    screens.ClientListScreenWidget.include({
        show: function() {
            var self = this;
            this._super();
            this.$('.new-customer').click(function(){
                var query=document.getElementById('searchbox').value
                var Number = /^[0-9]+$/;

                if((query.match(Number)))
                {
                    console.log('query is a number');
                    var phone = query
                }
                else
                {
                    var phone = ''
                }

                self.display_client_details('edit',{
                    'country_id': self.pos.company.country_id,

                    'phone':phone,
                });
            });

        },

    });


});
