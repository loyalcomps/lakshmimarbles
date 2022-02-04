# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class PosOrderLines(models.Model):
    _inherit = 'pos.order'


    @api.model
    def get_orderlines(self, ref):
        discount = 0
        subtotal=0
        result = []
        order = self.env['pos.order'].sudo().search([('id', '=', ref)], limit=1)
        lines = self.env['pos.order.line'].search([('order_id', '=', ref)])
        payment_line = self.env['account.bank.statement.line'].search ([('pos_statement_id', '=', ref)])
        payment_lines=[]
        order_details = {}
        change = 0
        payment_dict={}

        for payment in payment_line:
            if payment.amount > 0:
                print payment.journal_id.name
                print payment.journal_id.name
                payment_dict={

                    'name':payment.journal_id.name if payment.journal_id.name else " ",
                    'amount':payment.amount if payment.amount else " "

                }
                payment_lines.append(payment_dict)
            else:
                change += payment.amount




        for o in order:
            order_details ={
            'state_id':o.partner_id.state_id.name if o.partner_id.state_id.name else " ",
            'x_gstin':o.partner_id.x_gstin if o.partner_id.x_gstin else " ",
            'street': o.partner_id.street if o.partner_id.street else " ",
            'city':o.partner_id.city if o.partner_id.city else " ",
            'date_order': str(datetime.strptime(o.date_order, "%Y-%m-%d %H:%M:%S").date()),
            'is_gstin': True if o.partner_id.x_gstin else False,
            'invoice_id':o.invoice_id.id if o.invoice_id else False,
            'partner_id':o.partner_id.id if o.partner_id else False,
            'partner_name':o.partner_id.name if o.partner_id else False,
            'phone':o.partner_id.phone if o.partner_id.phone else False,
            'partner_barcode':o.partner_id.barcode if o.partner_id else False,
            'partner_vat':o.partner_id.vat if o.partner_id else False,
            'id':o.id,
            'name':o.pos_reference,
            'pos_reference':o.pos_reference,
            'tot_amount' : o.amount_total ,
            'tot_tax' : o.amount_tax ,
            'tot_without_tax' : o.amount_total-o.amount_tax,
            'loyalty_points': o.partner_id.loyalty_points if o.partner_id else 0,
            }



        for line in lines:
            tax_name = self.env["account.tax"].browse(line.tax_ids.ids).name if line.tax_ids else "None"

            new_vals = {
                'product_id': line.product_id.name,
                'product_mrp': line.product_mrp,
                'unit': line.product_id.uom_id.name,
                'qty': line.qty,
                'price_unit': '%.2f'%line.price_unit,
                'tax_name' : tax_name,
                'discount': '%.2f'%line.discount,
                'price_subtotal' : '%.2f'%line.price_subtotal,
                'tax' : line.price_subtotal_incl - line.price_subtotal if line.price_subtotal_incl != 0 else 0,
                'price_subtotal_incl' : '%.2f'%line.price_subtotal_incl,
                'tax_ids' : line.tax_ids.ids if line.tax_ids else False,
                }
            discount += (line.price_unit * line.qty * line.discount) / 100
            subtotal += line.price_subtotal_incl
            result.append(new_vals)

        taxwithout = {}
        details = {}
        detail = []
        tax = 0
        res={}



        for line in order:
            if line.invoice_id.tax_line_ids:

                res = []
                # keep track of taxes already processed
                done_taxes = []
                # loop the invoice.tax.line in reversal sequence
                for tax_line in sorted(line.invoice_id.tax_line_ids, key=lambda x: -x.sequence):
                    if tax_line.amount:
                        tax = tax_line.tax_id
                        invoice = line.invoice_id.invoice_line_ids
                        if tax.amount_type == "group":
                            for child_tax in tax.children_tax_ids:
                                done_taxes.append(child_tax.id)
                        for ta in tax:
                            for i in invoice:
                                detail.append({

                            'name': tax_line.name,
                            'amount': round(tax_line.amount,2),
                            # 'taxable': round((tax_line.base-tax_line.amount),2) ,
                            'taxable': round((i.price_subtotal), 2),

                            'kfc': round(tax_line.amount, 2) if ta.kfc_adjust==True else 0,


                        })



        # for line in lines:
        #
        #     if line.order_id.invoice_id.tax_line_ids:
        #
        #
        #         if line.order_id.invoice_id.tax_line_ids[0] not in details:
        #             details[line.order_id.invoice_id.tax_line_ids.ids[0]] = {'amount' : round(float(line.price_subtotal_incl - line.price_subtotal if line.price_subtotal_incl != 0 else 0),2),
        #                                             'name' : "",
        #                                             'taxable' : line.price_subtotal,
        #                                             }
        #         else:
        #             details[line.order_id.invoice_id.tax_line_ids.ids[0]]['amount'] += round(float(line.price_subtotal_incl - line.price_subtotal if line.price_subtotal_incl != 0 else 0),2)
        #             details[line.order_id.invoice_id.tax_line_ids.ids[0]]['taxable'] += line.price_subtotal
        #
        # for tax in details:
        #     detail.append({'amount':round(float(details[tax]['amount']),2),'name':details[tax]['name'],'taxable':round(float(details[tax]['taxable']),2)})

        return [result, discount, payment_lines, change,order_details,detail,subtotal]