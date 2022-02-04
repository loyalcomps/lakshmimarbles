from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
import datetime
from datetime import datetime

from xlsxwriter.utility import xl_range, xl_rowcol_to_cell
from openerp.tools.translate import _
from openerp import models, fields, api


class Qltyvendorwisepdf(models.AbstractModel):
    _name ='report.vendor_pandl_report.vendorwise_pandl_pdf'

    def get_vendor_wise(self, data,vendor_id):
        lines = []
        product=[]

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        product_ids = data['form']['product_id']


        if product_ids:
            invoice_ids = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start),
                 ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id), ('partner_id', '=', vendor_id),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid']),
                 ('product_id','in',product_ids)])
        else:
            invoice_ids = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start),
                 ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),('partner_id', '=', vendor_id),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])
        for invoice in invoice_ids:
            product_id = self.env['product.product'].search([('id','=',invoice.product_id.id)]).id
            if product_id not in product:
                product.append(product_id)

        sl=0
        for i in product:
            p_qty = 0
            p_amt = 0
            sl += 1
            for k in invoice_ids:
                if i == k.product_id.id:
                    p_amt += k.price_subtotal_taxinc
                    p_qty += k.quantity
            product_obj = self.env['product.product'].browse(i)
            for obj in product_obj:
                product_name = obj.name
                qty_onhand = obj.qty_available
                cost = obj.standard_price
                landing_cost = obj.landing_cost
            res = {
                'sl_no': sl,
                'product': product_name,
                'onhand':qty_onhand,
                'cost': cost,
                'landing_cost':landing_cost,
                'p_qty': p_qty,
                'purchase': p_amt,
            }
            lines.append(res)
        vendor_name = self.env["res.partner"].browse(vendor_id).name
        result = {
            'data': lines,
            'name': vendor_name,
        }

        if lines:
            return result
        else:
            return []

    def get_vendor_contact_wise(self, data,vendor_id):
        lines = []
        product=[]

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        product_id = data['form']['product_id']

        if product_id:
            invoice_ids = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start),
                 ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id), ('partner_id', '=', vendor_id),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid']),
                 ('product_id','in',product_id)])
        else:
            invoice_ids = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start),
                 ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id),('partner_id', '=', vendor_id),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])
        for invoice in invoice_ids:
            product_id = self.env['product.product'].search([('id','=',invoice.product_id.id)]).id
            if product_id not in product:
                product.append(product_id)

        sl=0
        for i in product:
            p_qty = 0
            p_amt = 0
            sl += 1
            for k in invoice_ids:
                if i == k.product_id.id:
                    p_amt += k.price_subtotal_taxinc
                    p_qty += k.quantity
            product_obj = self.env['product.product'].browse(i)
            for obj in product_obj:
                product_name = obj.name
                qty_onhand = obj.qty_available
                cost = obj.standard_price
                landing_cost = obj.landing_cost
            res = {
                'sl_no': sl,
                'product': product_name,
                'cost': cost,
                'onhand':qty_onhand,
                'landing_cost': landing_cost,
                'p_qty': p_qty,
                'purchase': p_amt,
            }
            lines.append(res)
        vendor_id = self.env["res.partner"].browse(vendor_id)
        for partner_id in vendor_id:
            vendor_name = partner_id.parent_id.name + "," + partner_id.name
        result = {
            'data': lines,
            'name': vendor_name,
        }
        if lines:
            return result
        else:
            return []

    def get_product_sale_info(self, data):
        lines = []
        product = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        product_ids = data['form']['product_id']
        vendor_ids = data['form']['vendor_id']
        vendor_contact_ids = data['form']['vendor_contact_id']
        vendor_list = vendor_ids + vendor_contact_ids

        if product_ids:
            product = product_ids
        else:

            invoice_ids = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start),
                 ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id), ('partner_id', 'in', vendor_list),
                 ('invoice_id.type', '=', 'in_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid'])])
            for invoice in invoice_ids:
                product_id = self.env['product.product'].search([('id', '=', invoice.product_id.id)]).id
                if product_id not in product:
                    product.append(product_id)

        if product:
            out_invoice_lines = self.env["account.invoice.line"].search(
                [('invoice_id.date_invoice', '>=', date_start), ('invoice_id.date_invoice', '<=', date_end),
                 ('company_id', '=', company_id), ('invoice_id.type', '=', 'out_invoice'),
                 ('invoice_id.state', 'in', ['open', 'paid']),
                 ('product_id', 'in', product)])
        sl = 0
        for i in product:
            s_amt = 0
            s_qty = 0
            sl += 1
            for l in out_invoice_lines:
                if i == l.product_id.id:
                    s_amt += l.price_subtotal_taxinc
                    s_qty += l.quantity
            product_name = self.env['product.product'].search([('id', '=', i)]).name
            average_sale_price = (s_amt / s_qty) if s_qty != 0 else 0
            res = {
                'sl_no': sl,
                'product': product_name,
                'average_sale_price': average_sale_price,
                's_qty': s_qty,
                'sale': s_amt,
            }
            if res['s_qty']:
                lines.append(res)

        if lines:
            return lines
        else:
            return []

    @api.model
    def render_html(self, docids, data=None, config_id=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        vendor_id = data['form']['vendor_id']
        vendor_contact_id = data['form']['vendor_contact_id']
        vendor_wise =[]
        vendor_contact_wise = []

        for vendor in vendor_id:
            value =self.get_vendor_wise(data,vendor)
            if value:
                vendor_wise.append(value)
        for vendor in vendor_contact_id:
            value = self.get_vendor_contact_wise(data, vendor)
            if value:
                vendor_contact_wise.append(value)

        sale_info = self.get_product_sale_info(data)
        # get_lines = self.get_lines(data)

        date_object_startdate = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_object_enddate = datetime.strptime(date_end, '%Y-%m-%d').date()


        docargs = {
            'doc_ids': self.ids,
            'date_start': date_object_startdate.strftime('%d-%m-%Y'),
            'date_end': date_object_enddate.strftime('%d-%m-%Y'),
            'vendor_id':vendor_id,
            'vendor_contact_id':vendor_contact_id,
            'data': data['form'],
            'vendor_wise': vendor_wise,
            'vendor_contact_wise':vendor_contact_wise,
            'sale_info':sale_info,

        }

        return self.env['report'].render('vendor_pandl_report.vendorwise_pandl_pdf', docargs)