# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################

from odoo import api, fields, models

class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    prevent_partial_payment = fields.Boolean(string="Don't Allow Partial Payment In POS")