odoo.define('pos_multi_barcodes.product_barcode', function (require) {
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;

     models.load_models([
     {
            model: 'product.barcode',
            fields: ['product_tmpl_id', 'quantity', 'list_price', 'uom_id', 'barcode', 'product_id','product_mrp'],
            domain: function (self) {
                return []
            },
            context: {'pos': true},
            loaded: function (self, barcodes) {
                self.barcodes = barcodes;
                self.barcodes_by_barcode = {};
                for (var i = 0; i < barcodes.length; i++) {
                    if (!barcodes[i]['product_id']) {
                        continue
                    }
                    if (!self.barcodes_by_barcode[barcodes[i]['barcode']]) {
                        self.barcodes_by_barcode[barcodes[i]['barcode']] = [barcodes[i]];
                    } else {
                        self.barcodes_by_barcode[barcodes[i]['barcode']].push(barcodes[i]);
                    }
                }
            }
        },

     ]);

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({

        scan_product: function (parsed_code) {
            var self = this;
            var product = this.db.get_product_by_barcode(parsed_code.base_code);
            var barcodes = this.barcodes_by_barcode[parsed_code.base_code];
            var selectedOrder = this.get_order();
            if (!selectedOrder) {
                return _super_posmodel.scan_product.apply(this, arguments);
            }
            if (product && barcodes) {
                var list = [{
                    'label': product['display_name']  + '| MRP: ' + product['product_mrp'] + '| PRICE: ' + product['list_price'] + ' | QTY: 1 ' + '| and Uoms: ' + product['uom_id'][1],
                    'item': product,
                }];
                for (var i = 0; i < barcodes.length; i++) {
                    var barcode = barcodes[i];
                    list.push({
                        'label': barcode['product_id'][1]  + '| MRP: ' + barcode['product_mrp'] + '| PRICE: ' + barcode['list_price'] + ' | QTY: ' + barcode['quantity'] + '| and Uoms: ' + barcode['uom_id'][1],
                        'item': barcode,
                    });
                }

                this.gui.show_popup('selection', {
                    title: _t('Select product'),
                    list: list,
                    confirm: function (item) {
                        var barcode;
                        var product;
                        var price;
                        if (item['product_id']) {
                            barcode = item;
                            product = self.db.product_by_id[barcode.product_id[0]]
                            var order_pricelist = selectedOrder.order_pricelist;
                            if (order_pricelist){
                                price=self.db.price_dict[order_pricelist.id][barcode.product_id[0]][barcode.id][0];
                            }
                            else{
                                price= barcode['list_price'];
                            }


                            selectedOrder.add_product(product, {
                                product_mrp: barcode['product_mrp'],
                                price: price,
                                quantity: barcode['quantity'],
                                barcode_id:barcode['id'],
                                extras: {
                                    uom_id: barcode['uom_id'][0]
                                }
                            });
                        } else {
                            product = item;
                            selectedOrder.add_product(product, {});
                        }
                    }
                });
                if (list.length > 0) {
                    return true;
                }
            } else if (!product && barcodes) {
                if (barcodes.length == 1) {
                    var barcode = barcodes[0]
                    var price;
                    var product = this.db.product_by_id[barcode['product_id'][0]];
                    var order_pricelist = selectedOrder.order_pricelist;
                    if (order_pricelist){
                        price=self.db.price_dict[order_pricelist.id][barcode.product_id[0]][barcode.id][0];
                    }
                    else{
                        price= barcode['list_price'];
                    }
                    if (product) {
                        selectedOrder.add_product(product, {
                            product_mrp: barcode['product_mrp'],
                            price: price,
                            quantity: barcode['quantity'],
                            barcode_id:barcode['id'],
                            extras: {
                                uom_id: barcode['uom_id'][0]
                            }
                        });
                        return true;
                    }
                } else if (barcodes.length > 1) {
                    // if multi items the same barcode, require cashier select
                    var list = [];
                    var price;
                    for (var i = 0; i < barcodes.length; i++) {
                        var barcode = barcodes[i];
                        list.push({
                            'label': barcode['product_id'][1] + '| MRP: ' + barcode['product_mrp'] + '| PRICE: ' + barcode['list_price'] + ' | QTY: ' + barcode['quantity'] + '| and Uoms: ' + barcode['uom_id'][1],
                            'item': barcode,
                        });
                    }
                    this.gui.show_popup('selection', {
                        title: _t('Select product'),
                        list: list,
                        confirm: function (barcode) {
                            var product = self.db.product_by_id[barcode['product_id'][0]];
                            var order_pricelist = selectedOrder.order_pricelist;
                            if (order_pricelist){
                                price=self.db.price_dict[order_pricelist.id][barcode.product_id[0]][barcode.id][0];
                            }
                            else{
                                price= barcode['list_price'];
                            }
                            if (product) {
                                selectedOrder.add_product(product, {

                                    price: price,
                                    product_mrp: barcode['product_mrp'],
                                    quantity: barcode['quantity'],
                                    barcode_id:barcode['id'],
                                    extras: {
                                        uom_id: barcode['uom_id'][0]
                                    }
                                });
                            }
                        }
                    });
                    if (list.length > 0) {
                        return true;
                    }
                }
            } else if (product && !barcodes) {
                return _super_posmodel.scan_product.apply(this, arguments);
            }
            else if (!product && !barcodes) {
                return _super_posmodel.scan_product.apply(this, arguments);
            }
        }
    });

    var _super_order = models.Order.prototype;

    models.Order = models.Order.extend({
        add_product: function (product, options) {
            var res = _super_order.add_product.apply(this, arguments);
            var selected_orderline = this.selected_orderline;
            options = options || {};
            if(options.barcode_id !== undefined){
                selected_orderline['barcode_id'] = options.barcode_id;
                selected_orderline.trigger('change', selected_orderline);
            }


            return res
        },

    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
        _super_orderline.initialize.call(this,attr,options);
        if (options.json) {
            this.init_from_JSON(options.json);
            return;
        }
        this.barcode_id = options.barcode_id;
        },
        set_multi_barcode_id: function(barcode_id){
            this.barcode_id = barcode_id;
        },
        get_multi_barcode_id: function(barcode_id){

            return this.barcode_id;
        },
//        clone: function(){
//            var orderline = _super_orderline.clone.call(this);
//            orderline.barcode_id = this.barcode_id;
//            return orderline;
//        },

    });
});