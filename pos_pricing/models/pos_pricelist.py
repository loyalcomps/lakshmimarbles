# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Linto C T(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api,_


class PosPriceList(models.Model):
    _name = 'pos.pricelist'

    def _get_default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string="Name", required=True)
    item_ids = fields.One2many('pos.pricelist.items', 'pos_pricelist_id', string="Pricelist Items")
    currency_id = fields.Many2one('res.currency', 'Currency', default=_get_default_currency_id, required=True)
    company_id = fields.Many2one('res.company', 'Company')
    barcode_id = fields.Many2one('product.barcode', store=True, string='Barcodes', )


class PosPricelistItems(models.Model):
    _name = 'pos.pricelist.items'

    _applied_on_field_map = {

        'product': ['product_tmpl_id','barcode_id'],
        'product_category': ['categ_id'],
    }
    _compute_price_field_map = {
        'fixed': ['fixed_price'],
        'percentage': ['percent_price'],

    }

    @api.one
    @api.depends('categ_id', 'product_tmpl_id', 'compute_price', 'fixed_price', \
                 'pos_pricelist_id', 'percent_price', )
    def _get_pricelist_item_name_price(self):
        if self.applied_on =='product_category' and self.categ_id:
            self.name = _("Category: %s") % (self.categ_id.name)
        elif self.applied_on =='product' and self.product_tmpl_id and self.barcode_id:
            self.name = self.product_tmpl_id.name+'-'+self.barcode_id.barcode
        elif self.applied_on =='product' and self.product_tmpl_id:
            self.name = self.product_tmpl_id.name
        elif self.applied_on =='global':
            self.name = _("All Products")





    name = fields.Char(string="Name", compute='_get_pricelist_item_name_price')
    pos_pricelist_id = fields.Many2one('pos.pricelist', string="Pricelist")
    applied_on = fields.Selection([('global', "Global"), ('product_category', 'Product Category'),
                                   ('product', 'Product')], string="Applied On", default='global', required=True)
    min_quantity = fields.Integer(string="Minimum Quantity")
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date End")
    compute_price = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')],
                                     string="Compute Price", default='fixed')
    fixed_price = fields.Float(string="Fixed Price")
    percent_price = fields.Float(string="Percentage")

    categ_id = fields.Many2one('product.category', string="Product Category")
    product_tmpl_id = fields.Many2one('product.template', string="Product")

    company_id = fields.Many2one('res.company', 'Company', readonly=True, related='pos_pricelist_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  readonly=True, related='pos_pricelist_id.currency_id', store=True)
    barcode_id = fields.Many2one('product.barcode', store=True, string='Barcodes', )

    @api.onchange('applied_on')
    def _onchange_applied_on(self):
        for applied_on, field in self._applied_on_field_map.iteritems():
            if self.applied_on != applied_on:
                for f in field:
                    setattr(self, f, False)

    @api.multi
    @api.onchange('product_tmpl_id')
    def product_tmpl_id_change(self):
        self.barcode_id = False
        if not self.product_tmpl_id:
            return {'domain': {'barcode_id': []}}
        domain = {'barcode_id': [('product_tmpl_id', '=', self.product_tmpl_id.id)]}
        result = {'domain': domain}
        return result

    @api.onchange('compute_price')
    def _onchange_compute_price(self):
        for compute_price, field in self._compute_price_field_map.iteritems():
            if self.compute_price != compute_price:
                for f in field:
                    setattr(self, f, 0.0)

class PriceListPartner(models.Model):
    _inherit = 'res.partner'

    pos_pricelist_id = fields.Many2one('pos.pricelist', string="POS Pricelist")