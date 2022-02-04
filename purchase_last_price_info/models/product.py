# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, fields, models,SUPERUSER_ID
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

# Confirmation msg box for ORIC
# from odoo.osv import fields,osv
# from odoo.tools.translate import _
# class thesis_approval_message_oric(osv.osv_memory):
#     _name = "thesis.approval.message.oric"
#     _columns={
#         'text': fields.text(),
#     }
# thesis_approval_message_oric()


# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#
#     @api.one
#     def _get_last_purchase(self):
#         """ Get last purchase price, last purchase date and last supplier """
#         lines = self.env['purchase.order.line'].search(
#             [('product_id', '=', self.id),
#              ('state', 'in', ['confirmed', 'done'])]).sorted(
#             key=lambda l: l.order_id.date_order, reverse=True)
#         self.last_purchase_date = lines[:1].order_id.date_order
#         self.last_purchase_price = lines[:1].price_unit
#         self.last_supplier_id = lines[:1].order_id.partner_id
#
#     last_purchase_price = fields.Float(
#         string='Last Purchase Price', compute='_get_last_purchase')
#     last_purchase_date = fields.Date(
#         string='Last Purchase Date', compute='_get_last_purchase')
#     last_supplier_id = fields.Many2one(
#         comodel_name='res.partner', string='Last Supplier',
#         compute='_get_last_purchase')

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    on_hand = fields.Float(string='On hand')

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        # onhand qty
        vals = {}
        vals['on_hand'] = self.product_id.qty_available
        self.update(vals)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    load_product = fields.Boolean(string="Load Product",default=False)

    @api.onchange('partner_id','load_product')
    def onchange_partner_id_add_product(self):
        self.order_line = False
        if not self.partner_id:
            return
        if self.load_product==False:
            return

        # text = """The case """ + str(
        #     self.case_no) + """ will be forward to VC for further Approval. Are you want to proceed."""
        # query = 'delete from thesis_approval_message_oric'
        # self.env.cr.execute(query)
        # value = self.env['thesis.approval.message.oric'].sudo().create({'text': text})
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Message',
        #     'res_model': 'thesis.approval.message.oric',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'target': 'new',
        #     # 'context':{'thesis_obj':self.id,'flag':'course Work completed'},
        #     'res_id': value.id
        # }


        result={}
        values = {}
        order_line_var = self.env['purchase.order.line']
        product_info=self.env['product.supplierinfo'].search([('name','=',self.partner_id.id)])
        for info in product_info:
            # product_id=self.env['product.product'].search([('product_tmpl_id','=',info.product_tmpl_id.id)]).id
            product = self.env['product.product'].search([('product_tmpl_id', '=', info.product_tmpl_id.id)])
            values = {

                'price_unit':info.price,

                'date_planned' : datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'product_qty' : 1.0
                }
            for prd in product:

                values['product_id'] = prd.id
                values['product_uom'] = info.product_uom.id or prd.uom_id.id

                values['on_hand'] = prd.qty_available
                values['hsn'] = prd.hsn
                values['product_mrp'] = prd.product_mrp
                values['barcode'] = prd.barcode
                values['brand_id'] = prd.brand_id
                values['category_id'] = prd.categ_id

            # result['domain'] = {'product_uom': [('category_id', '=', info.product_id.uom_id.category_id.id)]}

                product_lang = prd.with_context({
                    'lang': self.partner_id.lang,
                    'partner_id': self.partner_id.id,
                })
                values['name'] = product_lang.display_name
                if product_lang.description_purchase:
                    values['name'] += '\n' + product_lang.description_purchase

                fpos = self.fiscal_position_id
                if self.env.uid == SUPERUSER_ID:
                    company_id = self.env.user.company_id.id
                    values['taxes_id'] = fpos.map_tax(
                        prd.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
                else:
                    values['taxes_id'] = fpos.map_tax(prd.supplier_taxes_id)

                order_line_var1 = order_line_var.new(values)
                order_line_var += order_line_var1
            # order_line_var1._suggest_quantity()
            # order_line_var1._onchange_quantity()

        self.order_line += order_line_var



            # yield result











