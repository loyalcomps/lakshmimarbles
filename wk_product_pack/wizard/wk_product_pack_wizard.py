# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################


from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class product_pack_wizard(models.TransientModel):
	_name = 'product.pack.wizard'

	name = fields.Text('Description')
	product_name = fields.Many2one('product.product','Product',required=True)
	quantity =  fields.Float('Quantity', required=True)
	unit_price = fields.Float('Unit Price')
	delay = fields.Float('Delivery Load Time')
	taxes = fields.Many2one('account.tax','Taxes')

	def add_product_button(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		warning_msgs = ''
		line_pool = self.pool.get('sale.order.line')
		pack_id = self.browse(cr, uid, ids[0])
		if pack_id.product_name.taxes_id:
			taxes_id = pack_id.product_name.taxes_id.ids
		line_pool.create(cr, uid, {'order_id':context['active_id'],'product_id':pack_id.product_name.id,'tax_id':[(6, 0, taxes_id)],'product_uom_qty':pack_id.quantity}, context)
		return True


	def onchange_quantity_pack(self, cr, uid, ids, quantity=False, product_name=False, context=None):
		if context is None:
			context = {}
		if quantity:
			if product_name:
				pack_id = self.pool.get('product.product').browse(cr, uid, product_name,context)
				line_pool = self.pool.get('sale.order.line')
				for prod in pack_id.wk_product_pack:
					if quantity * prod.product_quantity > prod.product_name.virtual_available:
						warn_msg = _('You plan to sell %s but you have only  %s quantities of the product %s available, and the total quantity to sell is  %s !!'%(quantity, prod.product_name.virtual_available, prod.product_name.name,quantity * prod.product_quantity)) 
						raise Warning(('Configuration Error!'),(warn_msg))

	def get_unit_price_onchange(self, cr, uid, ids, product_name=False, context=None):
		if context is None:
			context = {}
		products = ""
		description=""
		product_obj = self.pool.get('product.product').browse(cr, uid, product_name)
		if product_name:
			list_price = product_obj.list_price
			if product_obj.wk_product_pack:
				for new_obj in product_obj.wk_product_pack:
					quantity = product_obj.wk_product_pack.product_quantity
					products += str(new_obj.product_name.name) + ",\t"
			else:
				products = "No product"
			if product_obj.description:
				descrpt = str(product_obj.description)
			else:
				descrpt = "No Description"
			description = "Pack Name:  " + str(product_obj.name) + "\n" + "Products:  "+ products +"\n" +"Description:\n" + "\t\t "+ descrpt
			return {'value': {'unit_price':list_price,
							  'name':description,
							  'quantity':quantity}
				   }




 