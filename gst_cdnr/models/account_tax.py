# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from odoo import models, api, fields
import logging
_logger = logging.getLogger(__name__)

''' Account Tax '''
class GST_AccountTax(models.Model):
    _inherit = 'account.tax'

    gst_type = fields.Selection([('gst','GST'),
                                ('ugst','UGST'),
                                ('sgst','SGST'),
                                ('utgst','UTGST'),
                                ('cgst','CGST'),
                                ('igst','IGST'),
                                ('none','Non-GST')],
                                default="none",
                                string="GST Type")


