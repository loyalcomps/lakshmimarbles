# -*- coding: utf-8 -*-

from odoo import models, fields, api



class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('x_gstin','partner_type')
    def kfc_partner_bool(self):
        for i in self:
            if not i.x_gstin and i.partner_type=="B2BUR":
                i.kfc_plot=True
            else:
                i.kfc_plot = False


    kfc_plot = fields.Boolean(string='KFC',compute=kfc_partner_bool,default=False,
                                  help='The loyalty points the user won as '
                                       'part of a Loyalty Program')
