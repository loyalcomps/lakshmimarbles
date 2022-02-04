odoo.define('pos_retail.screens', function (require) {

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var _t = core._t;
    var gui = require('point_of_sale.gui');
    var rpc = require('web.rpc');
    var qweb = core.qweb;

    screens.ProductListWidget.include({
        init: function (parent, options) {
            var self = this;
            this._super(parent, options);
//            this.pos.bind('product:change_price_list', function (products) {
//                for (var i = 0; i < products.length; i++) {
//                    var product = products[i];
//                    var $product_el = $("[data-product-id='" + product['id'] + "'] .price-tag");
//                    $product_el.html(self.format_currency(product['price']) + '/' + product['uom_id'][1]);
//                }
//                return true;
//            });
            this.pos.bind('product:updated', function (product_data) {
                // when product update data
                // when stock on hand product change
                // odoo version 11

                // odoo version 10
                if (self.pos.version['server_serie'] == "10.0") {
                    var product_list = self.pos.products;
                    self.pos.db.category_search_string = {};
                    if (!product_data['price']) {
                        product_data['price'] = product_data['list_price'];
                    }
                    // if this method called from sync stock product_tmpl_id is INT and made bug
                    // else if called created/updated from backend product_tmpl_id is array
                    if (product_data['product_tmpl_id'].length == undefined) {
                        product_data['product_tmpl_id'] = [product_data['product_tmpl_id'], product_data['display_name']];
                    }
                    var product_is_exsit = false;
                    for (var i = 0; i < product_list.length; i++) {
                        var product = product_list[i];
                        if (product['id'] == product_data['id']) {
                            product_list[i] = product_data;
                            product_is_exsit = true;
                        } else {
                            product['product_tmpl_id'] = [product['product_tmpl_id'], product['display_name']];
                        }
                    }
                    if (product_is_exsit == false) {
                        product_list.push(product_data);
                    }
                    self.pos.db.add_products(product_list);
                    // change old cache
                    // fix big bugs cache big images
                    var image_url = self.get_product_image_url(product_data);
                    var product_html = qweb.render('Product', {
                        widget: self,
                        product: product_data,
                        image_url: image_url
                    });
                    var product_node = document.createElement('div');
                    product_node.innerHTML = product_html;
                    product_node = product_node.childNodes[1];
                    self.product_cache.cache_node(product_data['id'], product_node);
                    var $product_el = $(".product-list " + "[data-product-id='" + product_data['id'] + "']");
                    if ($product_el) {
                        $product_el.replaceWith(product_html);
                    }
                }

            });
//            this.mouse_down = false;
//            this.moved = false;
//            this.auto_tooltip;
//            this.product_mouse_down = function (e) {
//                if (e.which == 1) {
//                    console.log('mouse down');
//                    $('#info_tooltip').remove();
//                    self.right_arrangement = false;
//                    self.moved = false;
//                    self.mouse_down = true;
//                    self.touch_start(this.dataset.productId, e.pageX, e.pageY);
//                }
//            };
//            this.product_mouse_move = function (e) {
//                console.log('mouse move');
//                if (self.mouse_down) {
//                    self.moved = true;
//                }
//            };
        },
//        touch_start: function (product_id, x, y) {
//            var self = this;
//            console.log(self.moved)
//            this.auto_tooltip = setTimeout(function () {
//                if (self.moved == false) {
//                    this.right_arrangement = false;
//                    var product = self.pos.db.get_product_by_id(parseInt(product_id));
//                    var inner_html = self.generate_html(product);
//                    $('.product-list-container').prepend(inner_html);
//                    $(".close_button").on("click", function () {
//                        $('#info_tooltip').remove();
//                    });
//                }
//            }, 30);
//        },
//        generate_html: function (product) {
//            var self = this;
//            var product_tooltip_html = qweb.render('product_tooltip', {
//                widget: self,
//                product: product,
//                field_load_check: self.pos.db.field_load_check
//            });
//            return product_tooltip_html;
//        },
//        touch_end: function () {
//            if (this.auto_tooltip) {
//                clearTimeout(this.auto_tooltip);
//            }
//        },
//
//        renderElement: function () {
//            var self = this;
//            this._super();
//            if (this.pos.config.tooltip) {
//                var caches = this.product_cache;
//                for (var cache_key in caches.cache) {
//                    var product_node = this.product_cache.get_node(cache_key);
//                    product_node.addEventListener('click', this.click_product_handler);
//                    product_node.addEventListener('mousedown', this.product_mouse_down);
//                    product_node.addEventListener('mousemove', this.product_mouse_move);
//                }
//                $(".product-list-scroller").scroll(function (event) {
//                    $('#info_tooltip').remove();
//                });
//            }
//            var products = [];
//            for (var i = 0; i < this.pos.products.length; i++) {
//                var product = this.pos.products[i];
//                var label = "";
//                if (product['default_code']) {
//                    label = '[' + product['default_code'] + ']'
//                }
//                if (product['barcode']) {
//                    label = '[' + product['barcode'] + ']'
//                }
//                if (product['display_name']) {
//                    label = '[' + product['display_name'] + ']'
//                }
//                if (product['description']) {
//                    label = '[' + product['description'] + ']'
//                }
//                products.push({
//                    value: product['id'],
//                    label: label
//                })
//            }
//            var $search_box = $('.product-screen .searchbox >input');
//            $search_box.autocomplete({
//                source: products,
//                select: function (event, ui) {
//                    if (ui && ui['item'] && ui['item']['value'])
//                        var product = self.pos.db.get_product_by_id(ui['item']['value']);
//                    setTimeout(function () {
//                        this.$('.searchbox input')[0].value = '';
//                    }, 10);
//                    if (product) {
//                        return self.pos.get_order().add_product(product);
//                    }
//
//                }
//            });
//        },


    });





});