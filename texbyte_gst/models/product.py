# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, fields, api

#import logging
#log = logging.getLogger(__name__)

''' product.template inherited class for GST '''
class Product_Template_GST(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(default='product')  #Default Stockable Product, requires 'stock' module
    hsncode = fields.Many2one('texbyte_gst.hsncode', string="HSN Code")


    """ Set the taxes for product from HSN on hsncode change """
    @api.onchange('hsncode')
    def _set_taxes_from_hsncode(self):
        #log.info("Template HSN:" + str(self.hsncode)+":"+str(self.hsncode.gst_tax_ids)+":"+str(self.hsncode.gst_supplier_tax_ids))
        self.taxes_id = self.hsncode.gst_tax_ids.filtered(lambda r: r.type_tax_use == 'sale' and r.gst_type == 'gst') + \
                        self.hsncode.gst_tax_ids.filtered(lambda r: r.type_tax_use == 'sale' and 'gst' not in r.gst_type ) or [] #Add CESS etc
        self.supplier_taxes_id = self.hsncode.gst_tax_ids.filtered(lambda r: r.type_tax_use == 'purchase' and r.gst_type == 'gst') + \
                                 self.hsncode.gst_tax_ids.filtered(lambda r: r.type_tax_use == 'purchase' and 'gst' not in r.gst_type ) or [] #Add CESS etc

    """ Just return the name (remove internal reference) """
    @api.multi
    def name_get(self):
        return [(template.id, template.name) for template in self]
