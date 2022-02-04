# -*- coding: utf-8 -*-
# Copyright© 2016 ICTSTUDIO <http://www.ictstudio.eu>
# License: LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import logging
from itertools import chain

from odoo import models, fields,tools, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class product_pricelist(models.Model):
    _inherit = 'product.pricelist'
    
    show_on_products = fields.Boolean(string="Display on product page")
    product_price = fields.Float(
            compute="get_product_price",
            inverse="_set_product_price",
            string="Price"
    )
    product_price_manual = fields.Boolean(
            compute="get_price_manual",
            # inverse="_set_price_manual",
            string="Manual Price",

    )
    product_id = fields.Integer(
            #comodel_name="product.product",
            compute="get_product_price",
            string="product_id"
    )

    @api.model
    def _get_product_id(self):
        product_id = False
        if self.env.context.get('product_template_id', False):
            product_tmpl = self.env['product.template'].browse(
                    [self.env.context.get('product_template_id')]
            )
            product_id = False
            if product_tmpl:
                product_tmpl_id = product_tmpl[0]
                if product_tmpl_id and product_tmpl_id.product_variant_ids:
                    product = product_tmpl_id.product_variant_ids[0]
                    if product:
                        product_id = product.id
        elif self.env.context.get('product_id', False):
            product_id = self.env.context.get('product_id')

        return product_id

    @api.multi
    def get_price_manual(self):
        for rec in self:
            rec._get_price_manual()


    @api.multi
    def _get_price_manual(self):
        product_id = self._get_product_id()

        if self._context.get('product_id') and \
                self.env['product.pricelist.item'].search(
                        [
                            ('pricelist_id', '=', self.id),
                            ('product_id', '=', self._context.get('product_id'))
                        ]
                ):
            self.product_price_manual = True
        if self._context.get('product_template_id') and \
                self.env['product.pricelist.item'].search(
                        [
                            ('pricelist_id', '=', self.id),
                            ('product_tmpl_id', '=', self._context.get('product_template_id'))
                        ]
                ):
            self.product_price_manual = True

    @api.multi
    def get_product_price(self):
        for rec in self:
            rec._get_product_price()

    @api.multi
    def _get_product_price(self):
        product_id = self._get_product_id()
        if product_id:

            s = self.price_get(
                    product_id, 1)
            self.product_price=s.get(self.id, 0.0
            )
            self.product_id = product_id

    def _set_product_price(self):
        # Real change takes place in price_set after inverse
        # method of pricelists object on product_template
        _logger.debug("Set Price: %s", self.product_price)


    @api.multi
    def remove_price_manual(self):
        for rec in self:
            rec._remove_price_manual()

    @api.multi
    def _remove_price_manual(self):
        # Real change takes place in price_set after inverse
        # method of pricelists object on product_template
        if self._context.get('product_template_id'):
            self.price_remove(self._context.get('product_template_id'))
        if self._context.get('product_id'):
            product = self.env['product.product'].browse(self._context.get('product_id'))
            self.price_remove(product.product_tmpl_id.id)


    def price_set(self, product_template, new_price):
        """
        Set the price of the product in current pricelist
        if different from price through  pricerules
        :param product_template: product_template object
        :param new_price: new price
        :return:
        """
        if new_price:

            items = self.env['product.pricelist.item'].search(
                    [
                        ('product_tmpl_id','=', product_template.id),
                        ('pricelist_id', '=', self.id),('barcode_id','=',False)
                    ]
            )
            # product_price_type_ids = self.env['product.price.type'].search(
            #         [
            #             ('field', '=', 'list_price')
            #         ]
            # )
            if not items:
                self.env['product.pricelist.item'].create(
                        {
                            # 'base': product_price_type_ids and product_price_type_ids[0].id,
                            'applied_on':'1_product',
                            'base':'list_price',
                            'compute_price':'fixed',
                            'sequence': 1,
                            'name': product_template.name,
                            'product_tmpl_id': product_template.id,
                            'pricelist_id': self.id,
                            'fixed_price': new_price,
                            # 'price_discount': -1
                        }
                )
            else:
                for item in items:
                    item.write(
                            {
                                # 'base': product_price_type_ids and product_price_type_ids[0].id,
                                'sequence': 1,
                                'name': product_template.name,
                                'product_tmpl_id': product_template.id,
                                'pricelist_id': self.id,
                                'fixed_price': new_price,
                                'price_discount': -1
                            }
                    )
            return True

    @api.model
    def price_remove(self, product_template_id):
        items = self.env['product.pricelist.item'].search(
                    [
                        ('product_tmpl_id', '=', product_template_id)
                    ]
        )
        _logger.debug("Items: %s", items)
        for item in items:
            _logger.debug("Remove Item: %s", item)
            item.unlink()

        return True

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        If date in context: Date of the pricelist (%Y-%m-%d)

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.today()
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in
                                    enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        self._cr.execute(
            'SELECT item.id '
            'FROM product_pricelist_item AS item '
            'LEFT JOIN product_category AS categ '
            'ON item.categ_id = categ.id '
            'WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))'
            'AND (item.product_id IS NULL OR item.product_id = any(%s))'
            'AND (item.categ_id IS NULL OR item.categ_id = any(%s)) '
            'AND (item.pricelist_id = %s) '
            'AND (item.date_start IS NULL OR item.date_start<=%s) '
            'AND (item.date_end IS NULL OR item.date_end>=%s)'
            'ORDER BY item.applied_on, item.min_quantity desc, categ.parent_left desc',
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))

        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.env['product.pricelist.item'].browse(item_ids)
        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['product.uom'].browse([self._context['uom']])._compute_quantity(qty,
                                                                                                                  product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute('list_price')[product.id]

            price_uom = self.env['product.uom'].browse([qty_uom_id])
            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.barcode_id:
                        continue
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (
                            product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.barcode_id:
                        continue
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)])[product.id][
                        0]  # TDE: 0 = price, 1 = rule
                    price = rule.base_pricelist_id.currency_id.compute(price_tmp, self.currency_id, round=False)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]

                convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'percentage':
                        price = (price - (price * (rule.percent_price / 100))) or 0.0
                    else:
                        # complete formula
                        price_limit = price
                        price = (price - (price * (rule.price_discount / 100))) or 0.0
                        if rule.price_round:
                            price = tools.float_round(price, precision_rounding=rule.price_round)

                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(rule.price_surcharge)
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(rule.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(rule.price_max_margin)
                            price = min(price, price_limit + price_max_margin)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                price = product.currency_id.compute(price, self.currency_id, round=False)

            results[product.id] = (price, suitable_rule and suitable_rule.id or False)

        return results
