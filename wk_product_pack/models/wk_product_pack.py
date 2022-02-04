# -*- coding: utf-8 -*-

from odoo import fields, models, exceptions, api
from odoo.tools.translate import _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class product_template(models.Model):
    _inherit = 'product.template'

    selection_list = [
        ('consu', 'Consumable'),
        ('service', 'Service')
    ]

    def _get_virtual_stock(self):
        res = {}
        qty_list = []
        if self.type == 'service' and self.is_pack:
            for pack_pdts in self.wk_product_pack:
                orig_qty = pack_pdts.product_name.qty_available
                pack_qty = pack_pdts.product_quantity
                virtual_qty = orig_qty / pack_qty
                qty_list.append(virtual_qty)
            if len(qty_list) > 0:
                sorted_list = sorted(qty_list)
                res[self.id] = sorted_list[0]
            else:
                res[self.id] = 0
        else:
            res[self.id] = 0
        return res

    def _get_product_type(self):
        res = {}
        return res

    is_pack = fields.Boolean('Is product pack')
    wk_product_pack = fields.One2many('product.pack', 'wk_product_template', 'Product pack')
    virtual_stock = fields.Integer("Virtual Stock", compute=_get_virtual_stock)
    pack_stock_management = fields.Selection(
        [('decrmnt_pack', 'Decrement Pack Only'), ('decrmnt_products', 'Decrement Products Only'),
         ('decrmnt_both', 'Decrement Both')], 'Pack Stock Management', default='decrmnt_products')

    @api.onchange('pack_stock_management')
    def select_type_default_pack_mgmnt_onchange(self):
        pk_dec = self.pack_stock_management
        if pk_dec == 'decrmnt_products':
            prd_type = 'service'
        elif pk_dec == 'decrmnt_both':
            prd_type = 'product'
        else:
            prd_type = 'consu'
        self.type = prd_type

    @api.model
    def create(self, vals):
        if vals.get('is_pack'):
            if not vals.get('wk_product_pack'):
                raise ValidationError('No products in this pack. Select atleast one product.')
        return super(product_template, self).create(vals)

    @api.onchange('type')
    def select_default_pack_mgmnt_onchange_type(self):
        if self.is_pack:
            prd_type = self.type
            if prd_type == 'service':
                pack_type = 'decrmnt_products'
            elif prd_type == 'product':
                pack_type = 'decrmnt_both'
            else:
                pack_type = 'decrmnt_pack'
            self.pack_stock_management = pack_type


class product_product(models.Model):
    _inherit = "product.product"

    @api.multi
    def _need_procurement(self):
        for product in self:
            if product.type == 'service' and product.is_pack:
                return True
        return super(product_product, self)._need_procurement()

    @api.onchange('pack_stock_management')
    def select_type_default_pack_mgmnt_onchange(self):
        pk_dec = self.pack_stock_management
        if pk_dec == 'decrmnt_products':
            prd_type = 'service'
        elif pk_dec == 'decrmnt_both':
            prd_type = 'product'
        else:
            prd_type = 'consu'
        self.type = prd_type


class product_pack(models.Model):
    _name = 'product.pack'

    product_name = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    product_quantity = fields.Float(string='Quantity', required=True, default=1)
    wk_product_template = fields.Many2one(comodel_name='product.template', string='Product pack')
    wk_image = fields.Binary(related='product_name.image_medium', string='Image', store=True)
    price = fields.Float(related='product_name.lst_price', string='Product Price')
    uom_id = fields.Many2one(related='product_name.uom_id', string="Unit of Measure", readonly="1")
    name = fields.Char(related='product_name.name', readonly="1")
    discount_amount = fields.Float('Discount')
    discount = fields.Float('Discount %', digits=(16, 2))

    @api.onchange('price', 'discount_amount')
    def _onchange_discount(self):
        if self.price and self.discount_amount:
            self.discount = (self.discount_amount * 100) / self.price


class sale_order(models.Model):
    _inherit = 'sale.order'

    def action_ship_create(self, cr, uid, ids, context=None):
        procurement_obj = self.env['procurement.order']
        sale_line_obj = self['sale.order'].browse(cr, uid, ids)
        vals = super(sale_order, self).action_ship_create(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            proc_ids = []
            for line in order.order_line:
                if line.product_id.is_pack:
                    line_data = self._prepare_order_line_procurement(cr, uid, order, line,
                                                                     order.procurement_group_id.id, context)
                    if line.product_id.pack_stock_management != 'decrmnt_pack':
                        for pack_obj in line.product_id.wk_product_pack:
                            temp = line_data
                            temp['product_id'] = pack_obj.product_name.id
                            temp['product_qty'] = line.product_uom_qty * pack_obj.product_quantity
                            temp['product_uom'] = pack_obj.product_name.uom_id.id
                            temp['product_uos_qty'] = pack_obj.product_name.uos_id.id
                            temp['sale_line_id'] = False
                            ctx = context.copy()
                            ctx['procurement_autorun_defer'] = True
                            proc_id = procurement_obj.create(cr, uid, temp, ctx)
                            proc_ids.append(proc_id)
                procurement_obj.run(cr, uid, proc_ids, context=context)
        return vals


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product, qty=0,
                                  uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                                  lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
                                  flag=False, warehouse_id=False, context=None):
        res = super(sale_order_line, self).product_id_change_with_wh(cr, uid, ids, pricelist, product, qty, uom,
                                                                     qty_uos, uos, name, partner_id, lang, update_tax,
                                                                     date_order, packaging, fiscal_position, flag,
                                                                     warehouse_id, context)
        warning = {}
        res_packing = self.product_packaging_change(cr, uid, ids, pricelist, product, qty, uom, partner_id, packaging,
                                                    context=context)
        res['value'].update(res_packing.get('value', {}))
        warning_msgs = res_packing.get('warning') and res_packing['warning']['message'] or ''
        if product:
            product_obj = self.pool.get('product.product').browse(cr, uid, product, context=context)
            if product_obj.is_pack:
                for pack_product in product_obj.wk_product_pack:
                    if qty * pack_product.product_quantity > pack_product.product_name.virtual_available:
                        warn_msg = _(
                            'You plan to sell %s but you have only  %s quantities of the product %s available, and the total quantity to sell is  %s !!' % (
                                qty, pack_product.product_name.virtual_available, pack_product.product_name.name,
                                qty * pack_product.product_quantity))
                        warning_msgs += _("Not enough stock ! : ") + warn_msg + "\n\n"
                        if warning_msgs:
                            warning = {
                                'title': _('Configuration Error!'),
                                'message': warning_msgs
                            }
                        return {'warning': warning}

        return super(sale_order_line, self).product_id_change_with_wh(cr, uid, ids, pricelist, product, qty, uom,
                                                                      qty_uos, uos, name, partner_id, lang, update_tax,
                                                                      date_order, packaging, fiscal_position, flag,
                                                                      warehouse_id, context)
