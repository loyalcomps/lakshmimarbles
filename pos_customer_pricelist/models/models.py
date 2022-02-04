# -*- coding: utf-8 -*-

from itertools import chain
from odoo import models, fields, api,tools
from odoo.exceptions import UserError

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    barcode_id = fields.Many2one('product.barcode', store=True, string='Barcodes',)

    @api.multi
    @api.onchange('product_tmpl_id')
    def product_tmpl_id_change(self):
        if not self.product_tmpl_id:
            return {'domain': {'barcode_id': []}}
        domain = {'barcode_id': [('product_tmpl_id', '=', self.product_tmpl_id.id)]}
        result = {'domain': domain}
        return result

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'barcode_id': []}}
        domain = {'barcode_id': [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)]}
        result = {'domain': domain}
        return result

class product_barcode(models.Model):
    _inherit = 'product.barcode'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.barcode + ' ' + '[' + str(record.list_price) + ']'
            result.append((record.id, name))
        return result

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def price_compute_multi_barcode(self, price_type,barcode_id, uom=False, currency=False, company=False):
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['product.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        products = self
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            products = self.with_context(force_company=company and company.id or self._context.get('force_company',
                                                                                                   self.env.user.company_id.id)).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:
            # prices[product.id] = product[price_type] or 0.0
            if price_type == 'list_price':
                list_price = self.env['product.barcode'].search([('id','=',barcode_id)]).list_price
                prices[product.id] += list_price

            if uom:
                prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[product.id] = product.currency_id.compute(prices[product.id], currency)

        return prices


class ProductProduct(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    def _compute_price_rule_multi_barcode(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        If date in context: Date of the pricelist (%Y-%m-%d)

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.context_today(self)
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
            price_uom = self.env['product.uom'].browse([qty_uom_id])
            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template

            price = product.price_compute('list_price')[product.id]


            for rule in items:

                if rule.min_quantity and qty_in_product_uom < rule.min_quantity :
                    continue
                if is_product_template:
                    if rule.barcode_id:
                        continue
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id :
                        continue
                    if rule.product_id and not (
                            product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id) :
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

            results[product.id] = {0:(price, suitable_rule and suitable_rule.id or False)}

            if product.barcode_ids:
                for barcode in product.barcode_ids:
                    price = barcode.list_price
                    for rule in items:
                        if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                            continue
                        if is_product_template:

                            if rule.barcode_id and rule.barcode_id.id != barcode.id:
                                continue
                            if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id :
                                continue
                            if rule.product_id and not (
                                    product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                                # product rule acceptable on template if has only one variant
                                continue
                        else:

                            if rule.barcode_id and rule.barcode_id.id != barcode.id:
                                continue
                            if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id :
                                continue
                            if rule.product_id and product.id != rule.product_id.id :
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
                            price_tmp = \
                            rule.base_pricelist_id._compute_price_rule_multi_barcode([(product, qty, partner)])[product.id][
                                0]  # TDE: 0 = price, 1 = rule
                            price = rule.base_pricelist_id.currency_id.compute(price_tmp, self.currency_id, round=False)
                        else:
                            # if base option is public price take sale price else cost price of product
                            # price_compute_multi_barcode returns the price in the context UoM, i.e. qty_uom_id
                            price = product.price_compute_multi_barcode(rule.base,barcode.id)[product.id]
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
                    if product.id in results and barcode.id:
                        results[product.id][barcode.id]=(price, suitable_rule and suitable_rule.id or False)
                    elif product.id and barcode.id:
                        results[product.id] = {barcode.id:(price, suitable_rule and suitable_rule.id or False)}





        return results

    def _compute_price_rule_multi_new(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Multi pricelist, multi products
        Returns: dict{product_id: dict{pricelist_id: (price, suitable_rule)} }"""
        if not self.ids:
            pricelists = self.search([])
        else:
            pricelists = self
        results = {}

        for pricelist in pricelists:
            results.setdefault(pricelist.id, {})
            subres = pricelist._compute_price_rule_multi_barcode(products_qty_partner, date=date, uom_id=uom_id)
            for product_id, barcode in subres.items():
                for key,price in barcode.items():
                    if product_id in results[pricelist.id]:
                        results[pricelist.id][product_id][key] = price
                    else:
                        results[pricelist.id][product_id] = {key:price}
                    # results[pricelist.id][product_id][2] = price
                    # results[pricelist.id][product_id][198] = 2

                # results[pricelist.id][product_id][2]=price
                s=0
            s=0

        return results



class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_price_by_pricelist(self, product):
        price_list = {}
        products = self.env['product.product'].browse(product['product_ids'])
        pricelists = self.env['product.pricelist'].search([])
        pricelists2 = self.env['product.pricelist']
        quantity = 1
        partner = False

        lists = zip()

        quantities = [quantity] * len(products)
        partners = [partner] * len(products)

        result = zip(products, quantities,partners)

        price_list2 = pricelists2._compute_price_rule_multi_new(result)

        # for pricelist in pricelists:
        #
        #
        #     pricelist_obj = pricelist._compute_price_rule(self, result)
        #     price_list[pricelist.id] = pricelist_obj
        return price_list2
        # get_products_price(self, quantities, partners)
        # price_list = {}
        # pricelist_items = self.env['product.pricelist.item'].search([])
        # for pricelist_item in pricelist_items :
        #     if pricelist_item.applied_on=='3_global':
        #         s=0

        # for i in product.product_ids:
        #
        #     pdct_obj=self.env['product.product'].browse(i)
        #     for j in pdct_obj:
        #         if j.
        #     pricelist
        # self.env['product.pricelist'].search([])

        return

class PosOrder(models.Model):
    _inherit = 'pos.order'


    @api.model
    def _order_fields(self, ui_order):
       order_fields = super(PosOrder, self)._order_fields(ui_order)
       order_fields['pricelist_id'] = ui_order.get('pricelist_id', False)
       return order_fields
