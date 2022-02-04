# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class PosOrderLines(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, default=_default_currency, track_visibility='always')

    @api.model
    def print_receipt(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'aek_browser_pdf',
            'params': {
                'report_name': 'order_reprinting_pos.report_pos_reciept_new',
                'ids': self.ids,
                'datas': ["bjhg,jh"],
            }
        }

    @api.model
    def get_details(self, ref):
        order_id = self.env['pos.order'].sudo().search([('pos_reference', '=', ref)], limit=1)
        return order_id.ids

    @api.model
    def get_orderlines(self, ref):
        discount = 0
        result = []
        order = self.env['pos.order'].sudo().search([('id', '=', ref)], limit=1)
        lines = self.env['pos.order.line'].search([('order_id', '=', ref)])
        payment_lines = []
        order_details = {}
        change = 0

        for o in order:
            order_details = {
                'date_order': str(datetime.strptime(o.date_order, "%Y-%m-%d %H:%M:%S").date()),
                'invoice_id': o.invoice_id.id if o.invoice_id else False,
                'partner_id': o.partner_id.id if o.partner_id else False,
                'partner_name': o.partner_id.name if o.partner_id else False,
                'partner_barcode': o.partner_id.barcode if o.partner_id else False,
                'partner_vat': o.partner_id.vat if o.partner_id else False,
                'id': o.id,
                'name': o.pos_reference,
                'pos_reference': o.pos_reference,
                'tot_amount': o.amount_total,
                'tot_tax': o.amount_tax,
                'tot_without_tax': o.amount_total - o.amount_tax,
            }

        for line in lines:
            tax_name = self.env["account.tax"].browse(line.tax_ids.ids).name if line.tax_ids else "None"

            new_vals = {
                'product_id': line.product_id.name,
                # 'product_mrp': line.product_id.product_mrp,
                'unit': line.product_id.uom_id.name,
                'qty': line.qty,
                'price_unit': line.price_unit,
                'tax_name': tax_name,
                'discount': line.discount,
                'price_subtotal': line.price_subtotal,
                'tax': line.price_subtotal_incl - line.price_subtotal if line.price_subtotal_incl != 0 else 0,
                'price_subtotal_incl': line.price_subtotal_incl,
                'tax_ids': line.tax_ids.ids if line.tax_ids else False,
            }
            discount += (line.price_unit * line.qty * line.discount) / 100
            result.append(new_vals)

        taxwithout = {}
        details = {}
        detail = []
        tax = 0

        for line in lines:

            if line.tax_ids:
                if line.tax_ids.ids[0] not in details:
                    details[line.tax_ids.ids[0]] = {'amount': round(
                        float(line.price_subtotal_incl - line.price_subtotal if line.price_subtotal_incl != 0 else 0),
                        2),
                                                    'name': self.env["account.tax"].browse(
                                                        line.tax_ids.ids).name if line.tax_ids else "None",
                                                    'taxable': line.price_subtotal,
                                                    }
                else:
                    details[line.tax_ids.ids[0]]['amount'] += round(
                        float(line.price_subtotal_incl - line.price_subtotal if line.price_subtotal_incl != 0 else 0),
                        2)
                    details[line.tax_ids.ids[0]]['taxable'] += line.price_subtotal

        for tax in details:
            detail.append({'amount': round(float(details[tax]['amount']), 2), 'name': details[tax]['name'],
                           'taxable': round(float(details[tax]['taxable']), 2)})

        return [result, discount, payment_lines, change, order_details, detail]
