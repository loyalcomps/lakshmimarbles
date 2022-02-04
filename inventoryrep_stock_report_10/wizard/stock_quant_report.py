# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from itertools import groupby
from operator import itemgetter
from collections import defaultdict


class WizardValuationStockInventory(models.TransientModel):
    _name = 'wizard.valuation.stock.inventory'
    _description = 'Wizard that opens the stock Inventory by Location'

    location_id = fields.Many2one('stock.location', string= 'Location',required=True)    
    product_categ_id = fields.Many2one('product.category', string= 'Category')
    product_sub_categ_id = fields.Many2one('product.category', string= 'Sub Category')
    line_ids = fields.One2many('wizard.valuation.stock.inventory.line','wizard_id',required=True,ondelete='cascade')

    @api.multi
    def print_pdf_stock_inventory(self,data):
        line_ids_all_categ = []
        line_ids_filterd_categ = []
        line_ids = []

        #Unlink All one2many Line Ids from same wizard
        for wizard_id in self.env['wizard.valuation.stock.inventory.line'].search([('wizard_id','=',self.id)]):
            if wizard_id.wizard_id.id == self.id:
                self.write({'line_ids': [(3, wizard_id.id)]})
        
        # Creating Temp dictionry for Product List
        if data["product_sub_categ_id"]:
            for resource in self.env['stock.quant'].search([('location_id','=',self.location_id.id)]):                
                if resource.product_id.categ_id.id ==  data["product_sub_categ_id"] or resource.product_id.categ_id.parent_id.id ==  data["product_sub_categ_id"]:
                    line_ids_filterd_categ.append({
                        'location_id': resource.location_id.id,
                        'product_id': resource.product_id.id,
                        'product_categ_id': resource.product_id.categ_id.parent_id.id,
                        'product_sub_categ_id': resource.product_id.categ_id.id,
                        'product_uom_id': resource.product_id.uom_id.id,
                        'qty': resource.qty,
                        'standard_price': resource.product_id.standard_price,                
                    })
        else:
            for resource in self.env['stock.quant'].search([('location_id','=',self.location_id.id)]):
                line_ids_all_categ.append({
                    'location_id': resource.location_id.id,
                    'product_id': resource.product_id.id,
                    'product_categ_id': resource.product_id.categ_id.parent_id.id,
                    'product_sub_categ_id': resource.product_id.categ_id.id,
                    'product_uom_id': resource.product_id.uom_id.id,
                    'qty': resource.qty,
                    'standard_price': resource.product_id.standard_price,                
                })

        if data["product_sub_categ_id"]:
            #Merging stock moves into single product item line
            grouper = itemgetter("product_id","product_categ_id","product_sub_categ_id","location_id", "product_uom_id" ,"standard_price")
            for key, grp in groupby(sorted(line_ids_filterd_categ, key = grouper), grouper):
                temp_dict = dict(zip(["product_id","product_categ_id","product_sub_categ_id", "location_id","product_uom_id", "standard_price"], key))
                temp_dict["qty"] = sum(item["qty"] for item in grp)
                temp_dict["amount"] =  temp_dict["standard_price"] * temp_dict["qty"]
                line_ids.append((0,0,temp_dict))
        else:
            #Merging stock moves into single product item line
            grouper = itemgetter("product_id","product_categ_id","product_sub_categ_id","location_id", "product_uom_id" ,"standard_price")
            for key, grp in groupby(sorted(line_ids_all_categ, key = grouper), grouper):
                temp_dict = dict(zip(["product_id","product_categ_id","product_sub_categ_id", "location_id","product_uom_id", "standard_price"], key))
                temp_dict["qty"] = sum(item["qty"] for item in grp)
                temp_dict["amount"] =  temp_dict["standard_price"] * temp_dict["qty"]
                line_ids.append((0,0,temp_dict))
            
        if len(line_ids) == 0:
            raise ValidationError(_('Material is not available on this location.'))
            
        #writing to One2many line_ids
        self.write({'line_ids':line_ids})
        context = {
            'lang': 'en_US', 
            'active_ids': [self.id],
        }
        return {
            'context': context,
            'data': None,
            'type': 'ir.actions.report.xml',
            'report_name': 'inventoryrep_stock_report_10.report_stock_inventory_location',
            'report_type': 'qweb-pdf',
            'report_file': 'inventoryrep_stock_report_10.report_stock_inventory_location',
            'name': 'Stock Inventory',
            'flags' : { 'action_buttons' : True},
        }
        
class WizardValuationStockInventoryLine(models.TransientModel):
    _name = 'wizard.valuation.stock.inventory.line'

    wizard_id = fields.Many2one('wizard.valuation.stock.inventory',required=True, ondelete='cascade')
    location_id = fields.Many2one('stock.location', 'Location')
    product_id = fields.Many2one('product.product', 'Product')
    product_categ_id = fields.Many2one('product.category', string= 'Category')
    product_sub_categ_id = fields.Many2one('product.category', string= 'Sub Category')
    product_uom_id = fields.Many2one('product.uom')
    qty = fields.Float('Quantity')
    standard_price = fields.Float('Rate')
    amount = fields.Float('Amount')
