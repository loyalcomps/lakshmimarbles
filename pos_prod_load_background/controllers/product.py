# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from openerp import models, fields, api, _

class product_product(models.Model):
    _inherit = 'product.product'

    @api.model
    def calculate_product(self):
        self._cr.execute("""
                        SELECT count(id) FROM PRODUCT_TEMPLATE where available_in_pos='t' and sale_ok='t'
                        """)
        total_product = self._cr.fetchall()
        return total_product

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: