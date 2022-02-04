from odoo import fields, models, api, _

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import float_is_zero, float_compare
import xlwt
import base64
import cStringIO
# from datetime import datetime
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

B2CL_INVOICE_AMT_LIMIT = 250000


class GSTInvoice3BWizard(models.TransientModel):
    _name = 'invoice.report.gstr3b.wizard'

    # fields to generate xls
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    # inv_type = fields.Selection([('cust_inv','Sales Invoice'),('vndr_bil','Purchase Invoice')],
    #                            default='cust_inv')

    # fields for download xls
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=128)

    sorted_invoices = []
    refund_invoices = []
    pos_sorted_invoices = []

    def get_valid_invoices(self):
        # Searching for customer invoices
        from_date = datetime.strptime(self.date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(self.date_to, '%Y-%m-%d').date()
        refund_invoice_ids = []
        # if self.inv_type == 'cust_inv':
        #    inv_domain = ('type', 'in', ('out_invoice', 'out_refund'))
        # else:
        #    inv_domain = ('type', 'in', ('in_invoice', 'in_refund'))

        # Get all invoices including canceled, refund and refunded
        self.all_invoices = self.env['account.invoice'].search(
            [('date_invoice', '>=', from_date), ('date_invoice', '<=', to_date),('state', 'in', ['paid', 'open'])])  # Customer Invoice & Vendor Bills
        # self.all_invoices = self.env['account.invoice'].search([('date_invoice','>=', from_date),('date_invoice','<=', to_date),inv_domain])
        # Canceled invoices
        self.caneceled_invoices = self.all_invoices.filtered(lambda i: i.state == 'cancel')
        # Refund invoices
        self.refund_invoices = self.all_invoices.filtered(
            lambda i: i.state != 'cancel' and i.refund_invoice_id)  # Skip canceled refunds
        # Refunded invoices
        self.refunded_invoices = self.all_invoices.filtered(
            lambda i: i.state != 'cancel' and i.id in self.refund_invoices.mapped('refund_invoice_id').ids)
        # Legitimate invoices -- other than canceled, refund and refunded
        # invoices = self.all_invoices.filtered(lambda i: i.id not in self.caneceled_invoices.ids + self.refund_invoices.ids + self.refunded_invoices.ids )
        invoices = self.all_invoices.filtered(
            lambda i: i.id not in self.caneceled_invoices.ids)

        self.sorted_invoices = invoices.sorted(key=lambda p: (p.date_invoice, p.number))

        filter = [
            ('date_order', '>=', fields.Datetime.to_string(
                datetime.combine(from_date, datetime.min.time()))),
            ('date_order', '<=', fields.Datetime.to_string(
                datetime.combine(to_date, datetime.max.time()))),
            ('state', 'in', ['paid', 'done']),
        ]

        pos_order_objects = self.env['pos.order'].search(filter)

        self.pos_sorted_invoices = pos_order_objects.sorted(key=lambda p: (p.date_order, p.name))

        # canceled_refund_invoices = []
        # for x in invoice_data:
        #    if x['refund_invoice_id']:
        #        canceled_refund_invoices.append(x)
        #        invoice_data.remove(x)
        # for x in canceled_refund_invoices:
        #    refunded_invoice = (y for y in invoice_data if y['id'] == x['refund_invoice_id'][0]).next() or None
        #    if refunded_invoice:
        #        canceled_refund_invoices.append(refunded_invoice)
        #        invoice_data.remove(refunded_invoice)
        # sorted_invoices = invoice_data.sorted(key=lambda p: (p.date_invoice, p.number))

        # invoice_data = self.env['account.invoice'].search_read([('date_invoice','>=', from_date),('date_invoice','<=', to_date),('refund_invoice_id', '!=', None)])
        # invoice_data = self.env['account.invoice'].search([('date_invoice','>=', from_date),('date_invoice','<=', to_date),('state', '!=', 'cancel'),('refund_invoice_id', '!=', None)])
        ##data with all Refunded invoices
        # for x in invoice_data:
        #    #if x['refund_invoice_id']:
        #    #    refund_invoice_ids.append(x['refund_invoice_id'][0])
        #    refund_invoice_ids.append(x.refund_invoice_id.id)

        ##invoices with filtering with date, non cancelled and not refunded
        # invoices = self.env['account.invoice'].search([('date_invoice','>=', from_date),('date_invoice','<=', to_date), ('state', '!=', 'cancel'), ('refund_invoice_id', '=', None), ('id', 'not in', refund_invoice_ids), inv_domain])
        # return sorted_invoices

    @api.multi
    def generate_gstr3b_report(self):
        # Error handling is not taken into consideraion
        self.ensure_one()
        fp = cStringIO.StringIO()
        xl_workbook = xlwt.Workbook(encoding='utf-8')

        from_date = datetime.strptime(self.date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(self.date_to, '%Y-%m-%d').date()

        # Get the invoices
        self.get_valid_invoices()

        self.generate_3b_report(xl_workbook)

        xl_workbook.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name': 'gstr3b_' + str(from_date) + '-' + str(to_date) + '.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.report.gstr3b.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    """ GSTR-3B Summary """

    def generate_3b_report(self, wb1):
        # Error handling is not taken into consideraion
        self.ensure_one()

        ws1 = wb1.add_sheet('GSTR-3B')
        fp = cStringIO.StringIO()

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 12 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, col + 1, col + 6, "GSTR-3B", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "GSTIN", sub_header_style)
        ws1.write(row, col + 2, self.env.user.company_id.x_gstin, sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Legal name of the registered person", sub_header_style)
        ws1.write(row, col + 2, self.env.user.company_id.name, sub_header_content_style)

        hsn_summary_data = {}
        outward_taxable_supplies = {'taxable_value': 0.0, 'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        outward_taxable_zero_rated = {'taxable_value': 0.0, 'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        outward_taxable_exempted = {'taxable_value': 0.0, 'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        outward_non_gst = {'taxable_value': 0.0, 'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        inward_reverse_charge = {'taxable_value': 0.0, 'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        import_goods = {'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        import_service = {'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        inward_isd = {'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        all_itc = {'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        itc_reversed_1 = {'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        itc_reversed_2 = {'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        ineligible_1 = {'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        ineligible_2 = {'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        inward_zero_gst = {'inter': 0.0, 'intra': 0.0}
        non_gst = {'inter': 0.0, 'intra': 0.0}
        interest = {'igst': 0.0, 'cgst': 0.0, 'sgst': 0.0, 'cess': 0.0}
        pos_unreg_comp_uin_igst = {}  # {PoS: Unreg_Taxable_Amt, Unreg_IGST, Composition_Taxable_Amt, Composition_IGST, UIN_Taxamble_Amt, UIN_IGST}

        for invoice in self.sorted_invoices:
            for invoice_line in invoice.invoice_line_ids:
                prod_id = invoice_line.product_id
                line_uom = invoice_line.uom_id
                line_qty = line_uom._compute_quantity(invoice_line.quantity, prod_id.uom_id)
                # line_amount = invoice_line.price_subtotal_signed
                if invoice_line.discount_amount and invoice_line.quantity != 0:
                    price = invoice_line.price_unit - (invoice_line.discount_amount / invoice_line.quantity)
                elif invoice_line.discount:
                    price = invoice_line.price_unit * (1 - (invoice_line.discount or 0.0) / 100.0)
                else:
                    price = invoice_line.price_unit
                # price = invoice_line.price_unit * (1 - (invoice_line.discount or 0.0) / 100.0)
                if invoice_line.invoice_id.inclusive:
                    line_taxes = invoice_line.invoice_line_tax_ids.with_context(price_include=True,
                                                                   include_base_amount=True).compute_all_inc(price,
                                                                                                             invoice_line.invoice_id.currency_id,
                                                                                                             invoice_line.quantity,
                                                                                                             product=prod_id,
                                                                                                             partner=invoice_line.invoice_id.partner_id)
                else:
                    line_taxes = invoice_line.invoice_line_tax_ids.compute_all(price,
                                                                           invoice_line.invoice_id.currency_id,
                                                                           invoice_line.quantity, prod_id,
                                                                           invoice_line.invoice_id.partner_id)
                total_excluded =0.0
                if invoice_line.invoice_line_tax_ids:
                        if line_taxes:
                            total_excluded = line_taxes.get('total_excluded') if invoice_line.invoice_id.type in ('out_invoice','in_invoice') else line_taxes.get('total_excluded')*-1
                else:
                    total_excluded = invoice_line.price_subtotal_signed

                if invoice_line.invoice_id.currency_id.name != 'INR':

                    total_excluded = total_excluded * invoice_line.invoice_id.currency_id.rate
                line_amount = round(total_excluded, 2)
                # _logger.info(line_taxes)
                igst_amount = cgst_amount = sgst_amount = cess_amount = 0.0
                for tax_line in line_taxes['taxes']:
                    # tax_obj = self.env['account.tax'].browse(tax_line['id'])
                    if 'IGST' in tax_line['name']:  # tax_obj.gst_type == 'igst':
                        igst_amount += tax_line['amount'] if invoice.type in ('out_invoice', 'in_invoice') else (
                                tax_line['amount'] * -1)
                    elif 'CGST' in tax_line['name']:  # tax_obj.gst_type == 'cgst':
                        cgst_amount += tax_line['amount'] if invoice.type in ('out_invoice', 'in_invoice') else (
                                tax_line['amount'] * -1)
                    elif 'SGST' in tax_line['name'] or 'UTGST' in tax_line['name']:  # tax_obj.gst_type == 'sgst':
                        sgst_amount += tax_line['amount'] if invoice.type in ('out_invoice', 'in_invoice') else (
                                tax_line['amount'] * -1)
                    else:
                        cess_amount += tax_line['amount'] if invoice.type in ('out_invoice', 'in_invoice') else (
                                tax_line['amount'] * -1)

                # cgst_amount = invoice_line.invoice_line_tax_ids.filtered(lambda r: r.gst_type == 'cgst').amount
                # sgst_amount = invoice_line.invoice_line_tax_ids.filtered(lambda r: r.gst_type == 'sgst').amount
                line_total_amount = invoice_line.price_subtotal + igst_amount + cgst_amount + sgst_amount + cess_amount
                # _logger.info(invoice_line.invoice_line_tax_ids)
                # if line_amount < 0:
                #     line_total_amount = line_total_amount * -1

                if line_amount < 0 and invoice.type in ('out_refund'):
                    line_total_amount = line_total_amount * -1
                if line_amount <0 and invoice.type in ('out_invoice') and line_amount != line_total_amount:
                    line_total_amount = line_total_amount * -1

                if invoice.type in ('out_invoice', 'out_refund'):  # Customer Invoice
                    if float_compare(line_total_amount, line_amount,
                                     precision_digits=2) > 0:  # Taxable item, not zero rated/nil rated/exempted
                        outward_taxable_supplies['taxable_value'] += line_amount
                        outward_taxable_supplies['igst'] += igst_amount
                        outward_taxable_supplies['cgst'] += cgst_amount
                        outward_taxable_supplies['sgst'] += sgst_amount
                        outward_taxable_supplies['cess'] += cess_amount

                        if invoice.partner_id.x_gstin:

                            if pos_unreg_comp_uin_igst.get(invoice.partner_id.x_gstin[0:2]):
                                if invoice.partner_id.composition:
                                    pos_unreg_comp_uin_igst[invoice.partner_id.x_gstin[0:2]][
                                        'comp_taxable_amt'] += line_amount
                                    pos_unreg_comp_uin_igst[invoice.partner_id.x_gstin[0:2]]['comp_igst'] += igst_amount
                                else:
                                    pos_unreg_comp_uin_igst[invoice.partner_id.x_gstin[0:2]][
                                        'unreg_taxable_amt'] += line_amount
                                    pos_unreg_comp_uin_igst[invoice.partner_id.x_gstin[0:2]][
                                        'unreg_igst'] += igst_amount
                            else:
                                if invoice.partner_id.composition:
                                    pos_unreg_comp_uin_igst[invoice.partner_id.x_gstin[0:2]] = {
                                        'unreg_taxable_amt': 0, 'unreg_igst': 0,
                                        'comp_taxable_amt': line_amount, 'comp_igst': igst_amount,
                                        'uin_taxable_amt': 0, 'uin_igst': 0}  # TODO: Handle Composition & UIN holders
                                else:
                                    pos_unreg_comp_uin_igst[invoice.partner_id.x_gstin[0:2]] = {
                                        'unreg_taxable_amt': line_amount, 'unreg_igst': igst_amount,
                                        'comp_taxable_amt': 0, 'comp_igst': 0,
                                        'uin_taxable_amt': 0, 'uin_igst': 0}  # TODO: Handle Composition & UIN holders
                        else:
                            if pos_unreg_comp_uin_igst.get(invoice.company_id.x_gstin[0:2]):
                                if invoice.partner_id.composition:
                                    pos_unreg_comp_uin_igst[invoice.company_id.x_gstin[0:2]][
                                        'comp_taxable_amt'] += line_amount
                                    pos_unreg_comp_uin_igst[invoice.company_id.x_gstin[0:2]]['comp_igst'] += igst_amount
                                else:
                                    pos_unreg_comp_uin_igst[invoice.company_id.x_gstin[0:2]][
                                        'unreg_taxable_amt'] += line_amount
                                    pos_unreg_comp_uin_igst[invoice.company_id.x_gstin[0:2]][
                                        'unreg_igst'] += igst_amount
                            else:
                                if invoice.partner_id.composition:
                                    pos_unreg_comp_uin_igst[invoice.company_id.x_gstin[0:2]] = {
                                        'unreg_taxable_amt': 0, 'unreg_igst': 0,
                                        'comp_taxable_amt': line_amount, 'comp_igst': igst_amount,
                                        'uin_taxable_amt': 0, 'uin_igst': 0}  # TODO: Handle Composition & UIN holders
                                else:
                                    pos_unreg_comp_uin_igst[invoice.company_id.x_gstin[0:2]] = {
                                        'unreg_taxable_amt': line_amount, 'unreg_igst': igst_amount,
                                        'comp_taxable_amt': 0, 'comp_igst': 0,
                                        'uin_taxable_amt': 0, 'uin_igst': 0}

                        # if pos_unreg_comp_uin_igst.get(invoice.place_of_supply):
                        #     pos_unreg_comp_uin_igst[invoice.place_of_supply]['unreg_taxable_amt'] += line_amount
                        #     pos_unreg_comp_uin_igst[invoice.place_of_supply]['unreg_igst'] += igst_amount
                        # else:
                        #     pos_unreg_comp_uin_igst[invoice.place_of_supply] = {'unreg_taxable_amt': line_amount, 'unreg_igst': igst_amount,
                        #                                                          'comp_taxable_amt': 0, 'comp_igst': 0,
                        #                                                          'uin_taxable_amt': 0, 'uin_igst': 0}    #TODO: Handle Composition & UIN holders

                    else:  # Tream them all as zero rated for now
                        outward_taxable_zero_rated['taxable_value'] += line_amount
                        outward_taxable_zero_rated['igst'] += igst_amount
                        outward_taxable_zero_rated['cgst'] += cgst_amount
                        outward_taxable_zero_rated['sgst'] += sgst_amount
                        outward_taxable_zero_rated['cess'] += cess_amount

                # TODO: Vendor Bills with reverse charge doesn't have tax lines filled, so it must be calculated
                elif invoice.type in (
                        'in_invoice',
                        'in_refund'):  # and invoice.reverse_charge: #Vendor Bills with Reverse Charge applicablle
                    # if invoice.reverse_charge:
                    if not invoice.partner_id.x_gstin:
                        inward_reverse_charge['taxable_value'] += line_amount
                        inward_reverse_charge['igst'] += igst_amount
                        inward_reverse_charge['cgst'] += cgst_amount
                        inward_reverse_charge['sgst'] += sgst_amount
                        inward_reverse_charge['cess'] += cess_amount
                    else:
                        if float_compare(line_total_amount, line_amount, precision_digits=2) == 0:  # Zero GST taxes
                            # if invoice.place_of_supply != invoice.company_id.place_of_supply:
                            if invoice.partner_id.x_gstin:
                                if invoice.partner_id.x_gstin[0:2] != invoice.company_id.x_gstin[0:2]:
                                    inward_zero_gst['inter'] += line_amount
                                else:
                                    inward_zero_gst['intra'] += line_amount
                            else:
                                inward_zero_gst['intra'] += line_amount
                        else:  # Taxable purchase, eligible for ITC
                            all_itc['igst'] += igst_amount
                            all_itc['cgst'] += cgst_amount
                            all_itc['sgst'] += sgst_amount
                            all_itc['cess'] += cess_amount

        # _logger.info(hsn_summary_data)

        for pos in self.pos_sorted_invoices:
            for pos_line in pos.lines:
                prod_id = pos_line.product_id
                line_uom = prod_id.uom_id
                line_qty = line_uom._compute_quantity(pos_line.qty, prod_id.uom_id)
                line_amount = pos_line.price_subtotal
                line_taxes = pos_line.tax_ids.compute_all(pos_line.price_unit,
                                                                       pos_line.order_id.pricelist_id.currency_id,
                                                                       pos_line.qty, prod_id,
                                                                       pos_line.order_id.partner_id)
                # _logger.info(line_taxes)
                igst_amount = cgst_amount = sgst_amount = cess_amount = 0.0
                for tax_line in line_taxes['taxes']:
                    # tax_obj = self.env['account.tax'].browse(tax_line['id'])
                    if 'IGST' in tax_line['name']:  # tax_obj.gst_type == 'igst':
                        igst_amount += tax_line['amount'] if pos.amount_total > 0 else (
                                tax_line['amount'] * -1)
                    elif 'CGST' in tax_line['name']:  # tax_obj.gst_type == 'cgst':
                        cgst_amount += tax_line['amount'] if pos.amount_total > 0 else (
                                tax_line['amount'] * -1)
                    elif 'SGST' in tax_line['name'] or 'UTGST' in tax_line['name']:  # tax_obj.gst_type == 'sgst':
                        sgst_amount += tax_line['amount'] if pos.amount_total > 0 else (
                                tax_line['amount'] * -1)
                    else:
                        cess_amount += tax_line['amount'] if pos.amount_total > 0 else (
                                tax_line['amount'] * -1)

                line_total_amount = pos_line.price_subtotal + igst_amount + cgst_amount + sgst_amount + cess_amount

                if float_compare(line_total_amount, line_amount,
                                 precision_digits=2) > 0:

                    outward_taxable_supplies['taxable_value'] += line_amount
                    outward_taxable_supplies['igst'] += igst_amount
                    outward_taxable_supplies['cgst'] += cgst_amount
                    outward_taxable_supplies['sgst'] += sgst_amount
                    outward_taxable_supplies['cess'] += cess_amount

                    if pos.partner_id.x_gstin:

                        if pos_unreg_comp_uin_igst.get(pos.partner_id.x_gstin[0:2]):
                            if pos.partner_id.composition:
                                pos_unreg_comp_uin_igst[pos.partner_id.x_gstin[0:2]][
                                    'comp_taxable_amt'] += line_amount
                                pos_unreg_comp_uin_igst[pos.partner_id.x_gstin[0:2]]['comp_igst'] += igst_amount
                            else:
                                pos_unreg_comp_uin_igst[pos.partner_id.x_gstin[0:2]][
                                    'unreg_taxable_amt'] += line_amount
                                pos_unreg_comp_uin_igst[pos.partner_id.x_gstin[0:2]][
                                    'unreg_igst'] += igst_amount
                        else:
                            if pos.partner_id.composition:
                                pos_unreg_comp_uin_igst[pos.partner_id.x_gstin[0:2]] = {
                                    'unreg_taxable_amt': 0, 'unreg_igst': 0,
                                    'comp_taxable_amt': line_amount, 'comp_igst': igst_amount,
                                    'uin_taxable_amt': 0, 'uin_igst': 0}  # TODO: Handle Composition & UIN holders
                            else:
                                pos_unreg_comp_uin_igst[pos.partner_id.x_gstin[0:2]] = {
                                    'unreg_taxable_amt': line_amount, 'unreg_igst': igst_amount,
                                    'comp_taxable_amt': 0, 'comp_igst': 0,
                                    'uin_taxable_amt': 0, 'uin_igst': 0}  # TODO: Handle Composition & UIN holders
                    else:
                        if pos_unreg_comp_uin_igst.get(pos.company_id.x_gstin[0:2]):
                            if pos.partner_id.composition:
                                pos_unreg_comp_uin_igst[pos.company_id.x_gstin[0:2]][
                                    'comp_taxable_amt'] += line_amount
                                pos_unreg_comp_uin_igst[pos.company_id.x_gstin[0:2]]['comp_igst'] += igst_amount
                            else:
                                pos_unreg_comp_uin_igst[pos.company_id.x_gstin[0:2]][
                                    'unreg_taxable_amt'] += line_amount
                                pos_unreg_comp_uin_igst[pos.company_id.x_gstin[0:2]][
                                    'unreg_igst'] += igst_amount
                        else:
                            if pos.partner_id.composition:
                                pos_unreg_comp_uin_igst[pos.company_id.x_gstin[0:2]] = {
                                    'unreg_taxable_amt': 0, 'unreg_igst': 0,
                                    'comp_taxable_amt': line_amount, 'comp_igst': igst_amount,
                                    'uin_taxable_amt': 0, 'uin_igst': 0}  # TODO: Handle Composition & UIN holders
                            else:
                                pos_unreg_comp_uin_igst[pos.company_id.x_gstin[0:2]] = {
                                    'unreg_taxable_amt': line_amount, 'unreg_igst': igst_amount,
                                    'comp_taxable_amt': 0, 'comp_igst': 0,
                                    'uin_taxable_amt': 0, 'uin_igst': 0}
                else:
                    outward_taxable_zero_rated['taxable_value'] += line_amount
                    outward_taxable_zero_rated['igst'] += igst_amount
                    outward_taxable_zero_rated['cgst'] += cgst_amount
                    outward_taxable_zero_rated['sgst'] += sgst_amount
                    outward_taxable_zero_rated['cess'] += cess_amount


        row += 2

        # Innter functions
        def prepare_outward_supplies(row):
            ws1.write_merge(row, row, col + 1, col + 6,
                            "3.1 Details of Outward Supplies and inward supplies liable to reverse charge",
                            sub_header_style)
            row += 1
            ws1.write(row, col + 1, "Nature of Supplies", sub_header_style)
            ws1.write(row, col + 2, "Taxable Value", sub_header_style)
            ws1.write(row, col + 3, "IGST", sub_header_style)
            ws1.write(row, col + 4, "CGST", sub_header_style)
            ws1.write(row, col + 5, "SGST", sub_header_style)
            ws1.write(row, col + 6, "Cess", sub_header_style)

            ws1.write(row + 1, col + 1,
                      "(a) Outward Taxable  supplies  (other than zero rated, nil rated and exempted)",
                      line_content_style)
            ws1.write(row + 2, col + 1, "(b) Outward Taxable  supplies  (zero rated )", line_content_style)
            ws1.write(row + 3, col + 1, "(c) Other Outward Taxable  supplies (Nil rated, exempted)", line_content_style)
            ws1.write(row + 4, col + 1, "(d) Inward supplies (liable to reverse charge)", line_content_style)
            ws1.write(row + 5, col + 1, "(e) Non-GST Outward supplies", line_content_style)

            ws1.write(row + 1, col + 2, outward_taxable_supplies['taxable_value'], line_content_style)
            ws1.write(row + 2, col + 2, outward_taxable_zero_rated['taxable_value'], line_content_style)
            ws1.write(row + 3, col + 2, outward_taxable_exempted['taxable_value'], line_content_style)
            ws1.write(row + 4, col + 2, inward_reverse_charge['taxable_value'], line_content_style)
            ws1.write(row + 5, col + 2, outward_non_gst['taxable_value'], line_content_style)

            ws1.write(row + 1, col + 3, outward_taxable_supplies['igst'], line_content_style)
            ws1.write(row + 2, col + 3, outward_taxable_zero_rated['igst'], line_content_style)
            ws1.write(row + 3, col + 3, outward_taxable_exempted['igst'], line_content_style)
            ws1.write(row + 4, col + 3, inward_reverse_charge['igst'], line_content_style)
            ws1.write(row + 5, col + 3, outward_non_gst['igst'], line_content_style)

            ws1.write(row + 1, col + 4, outward_taxable_supplies['cgst'], line_content_style)
            ws1.write(row + 2, col + 4, outward_taxable_zero_rated['cgst'], line_content_style)
            ws1.write(row + 3, col + 4, outward_taxable_exempted['cgst'], line_content_style)
            ws1.write(row + 4, col + 4, inward_reverse_charge['cgst'], line_content_style)
            ws1.write(row + 5, col + 4, outward_non_gst['cgst'], line_content_style)

            ws1.write(row + 1, col + 5, outward_taxable_supplies['sgst'], line_content_style)
            ws1.write(row + 2, col + 5, outward_taxable_zero_rated['sgst'], line_content_style)
            ws1.write(row + 3, col + 5, outward_taxable_exempted['sgst'], line_content_style)
            ws1.write(row + 4, col + 5, inward_reverse_charge['sgst'], line_content_style)
            ws1.write(row + 5, col + 5, outward_non_gst['sgst'], line_content_style)

            ws1.write(row + 1, col + 6, outward_taxable_supplies['cess'], line_content_style)
            ws1.write(row + 2, col + 6, outward_taxable_zero_rated['cess'], line_content_style)
            ws1.write(row + 3, col + 6, outward_taxable_exempted['cess'], line_content_style)
            ws1.write(row + 4, col + 6, inward_reverse_charge['cess'], line_content_style)
            ws1.write(row + 5, col + 6, outward_non_gst['cess'], line_content_style)

            row += 8
            return row

        def prepare_eligible_itc(row):

            ws1.write_merge(row, row, col + 1, col + 5, "4. Eligible ITC", sub_header_style)
            row += 1
            ws1.write(row, col + 1, "Details", sub_header_style)
            ws1.write(row, col + 2, "Integrated Tax", sub_header_style)
            ws1.write(row, col + 3, "Central Tax", sub_header_style)
            ws1.write(row, col + 4, "State/UT Tax", sub_header_style)
            ws1.write(row, col + 5, "CESS", sub_header_style)

            ws1.write(row + 1, col + 1, "(A) ITC Available (Whether in full or part)", line_content_style)
            ws1.write(row + 2, col + 1, "   (1) Import of goods", line_content_style)
            ws1.write(row + 3, col + 1, "   (2) Import of services", line_content_style)
            ws1.write(row + 4, col + 1, "   (3) Inward supplies liable to reverse charge(other than 1 &2 above)",
                      line_content_style)
            ws1.write(row + 5, col + 1, "   (4) Inward supplies from ISD", line_content_style)
            ws1.write(row + 6, col + 1, "   (5) All other ITC", line_content_style)
            ws1.write(row + 7, col + 1, "(B) ITC Reversed", line_content_style)
            ws1.write(row + 8, col + 1, "   (1) As per Rule 42 & 43 of SGST/CGST rules", line_content_style)
            ws1.write(row + 9, col + 1, "   (2) Others", line_content_style)
            ws1.write(row + 10, col + 1, "(C) Net ITC Available (A)-(B)", line_content_style)
            ws1.write(row + 11, col + 1, "(D) Ineligible ITC", line_content_style)
            ws1.write(row + 12, col + 1, "  (1) As per section 17(5) of CGST/SGST Act", line_content_style)
            ws1.write(row + 13, col + 1, "  (2) Others", line_content_style)

            ws1.write(row + 2, col + 2, import_goods['igst'], line_content_style)
            ws1.write(row + 3, col + 2, import_service['igst'], line_content_style)
            ws1.write(row + 4, col + 2, inward_reverse_charge['igst'], line_content_style)
            ws1.write(row + 5, col + 2, inward_isd['igst'], line_content_style)
            ws1.write(row + 6, col + 2, all_itc['igst'], line_content_style)
            ws1.write(row + 8, col + 2, itc_reversed_1['igst'], line_content_style)
            ws1.write(row + 9, col + 2, itc_reversed_2['igst'], line_content_style)
            ws1.write(row + 11, col + 2, ineligible_1['igst'], line_content_style)
            ws1.write(row + 12, col + 2, ineligible_2['igst'], line_content_style)

            ws1.write(row + 2, col + 3, import_goods['cgst'], line_content_style)
            ws1.write(row + 3, col + 3, import_service['cgst'], line_content_style)
            ws1.write(row + 4, col + 3, inward_reverse_charge['cgst'], line_content_style)
            ws1.write(row + 5, col + 3, inward_isd['cgst'], line_content_style)
            ws1.write(row + 6, col + 3, all_itc['cgst'], line_content_style)
            ws1.write(row + 8, col + 3, itc_reversed_1['cgst'], line_content_style)
            ws1.write(row + 9, col + 3, itc_reversed_2['cgst'], line_content_style)
            ws1.write(row + 11, col + 3, ineligible_1['cgst'], line_content_style)
            ws1.write(row + 12, col + 3, ineligible_2['cgst'], line_content_style)

            ws1.write(row + 2, col + 4, import_goods['sgst'], line_content_style)
            ws1.write(row + 3, col + 4, import_service['sgst'], line_content_style)
            ws1.write(row + 4, col + 4, inward_reverse_charge['sgst'], line_content_style)
            ws1.write(row + 5, col + 4, inward_isd['sgst'], line_content_style)
            ws1.write(row + 6, col + 4, all_itc['sgst'], line_content_style)
            ws1.write(row + 8, col + 4, itc_reversed_1['sgst'], line_content_style)
            ws1.write(row + 9, col + 4, itc_reversed_2['sgst'], line_content_style)
            ws1.write(row + 11, col + 4, ineligible_1['sgst'], line_content_style)
            ws1.write(row + 12, col + 4, ineligible_2['sgst'], line_content_style)

            ws1.write(row + 2, col + 5, import_goods['cess'], line_content_style)
            ws1.write(row + 3, col + 5, import_service['cess'], line_content_style)
            ws1.write(row + 4, col + 5, inward_reverse_charge['cess'], line_content_style)
            ws1.write(row + 5, col + 5, inward_isd['cess'], line_content_style)
            ws1.write(row + 6, col + 5, all_itc['cess'], line_content_style)
            ws1.write(row + 8, col + 5, itc_reversed_1['cess'], line_content_style)
            ws1.write(row + 9, col + 5, itc_reversed_2['cess'], line_content_style)
            ws1.write(row + 11, col + 5, ineligible_1['cess'], line_content_style)
            ws1.write(row + 12, col + 5, ineligible_2['cess'], line_content_style)

            row += 16
            return row

        def prepare_exempt_supplies(row):

            ws1.write_merge(row, row, col + 1, col + 3, "5. Values of exempt, Nil-rated and non-GST inward supplies",
                            sub_header_style)
            row += 1
            ws1.write(row, col + 1, "Nature of supplies", sub_header_style)
            ws1.write(row, col + 2, "Inter-State Supplies", sub_header_style)
            ws1.write(row, col + 3, "Intra-State Supplies", sub_header_style)

            ws1.write(row + 1, col + 1, "From a supplier under composition scheme, Exempt  and Nil rated supply",
                      line_content_style)
            ws1.write(row + 2, col + 1, "Non-GST Supply", line_content_style)

            ws1.write(row + 1, col + 2, inward_zero_gst['inter'], line_content_style)
            ws1.write(row + 2, col + 2, non_gst['inter'], line_content_style)

            ws1.write(row + 1, col + 3, inward_zero_gst['intra'], line_content_style)
            ws1.write(row + 2, col + 3, non_gst['intra'], line_content_style)

            row += 5
            return row

        def prepare_interest_late_fee(row):

            ws1.write_merge(row, row, col + 1, col + 5, "5.1 Interest & late fee payable", sub_header_style)
            row += 1
            ws1.write(row, col + 1, "Description", sub_header_style)
            ws1.write(row, col + 2, "Integrated Tax", sub_header_style)
            ws1.write(row, col + 3, "Central Tax", sub_header_style)
            ws1.write(row, col + 4, "State/UT Tax", sub_header_style)
            ws1.write(row, col + 5, "CESS", sub_header_style)

            ws1.write(row + 1, col + 1, 'Interest', line_content_style)
            ws1.write(row + 1, col + 2, interest['igst'], line_content_style)
            ws1.write(row + 1, col + 3, interest['cgst'], line_content_style)
            ws1.write(row + 1, col + 4, interest['sgst'], line_content_style)
            ws1.write(row + 1, col + 5, interest['cess'], line_content_style)

            row += 4
            return row

        def prepare_inter_state_unreg(row):

            ws1.write_merge(row, row, col + 1, col + 7,
                            "3.2  Of the supplies shown in 3.1 (a), details of inter-state supplies made to unregistered persons, composition taxable person and UIN holders",
                            sub_header_style)
            row += 1
            ws1.write_merge(row, row + 1, col + 1, col + 1, "Place of Supply(State/UT)", sub_header_style)
            ws1.write_merge(row, row, col + 2, col + 3, "Supplies made to Unregistered Persons", sub_header_style)
            ws1.write_merge(row, row, col + 4, col + 5, "Supplies made to Composition Taxable Persons",
                            sub_header_style)
            ws1.write_merge(row, row, col + 6, col + 7, "Supplies made to UIN holders", sub_header_style)
            ws1.write(row + 1, col + 2, "Total Taxable value", sub_header_style)
            ws1.write(row + 1, col + 3, "Amount of Integrated Tax", sub_header_style)
            ws1.write(row + 1, col + 4, "Total Taxable value", sub_header_style)
            ws1.write(row + 1, col + 5, "Amount of Integrated Tax", sub_header_style)
            ws1.write(row + 1, col + 6, "Total Taxable value", sub_header_style)
            ws1.write(row + 1, col + 7, "Amount of Integrated Tax", sub_header_style)
            ws1.write(row + 2, col + 1, "1", sub_header_style)
            ws1.write(row + 2, col + 2, "2", sub_header_style)
            ws1.write(row + 2, col + 3, "3", sub_header_style)
            ws1.write(row + 2, col + 4, "4", sub_header_style)
            ws1.write(row + 2, col + 5, "5", sub_header_style)
            ws1.write(row + 2, col + 6, "6", sub_header_style)
            ws1.write(row + 2, col + 7, "7", sub_header_style)

            row += 2
            for place_of_supply, tx_line in pos_unreg_comp_uin_igst.items():
                row += 1
                # ws1.write(row, col+1, place_of_supply.name_get()[0][1], line_content_style)
                ws1.write(row, col + 1, place_of_supply, line_content_style)
                ws1.write(row, col + 2, tx_line['unreg_taxable_amt'], line_content_style)
                ws1.write(row, col + 3, tx_line['unreg_igst'], line_content_style)
                ws1.write(row, col + 4, tx_line['comp_taxable_amt'], line_content_style)
                ws1.write(row, col + 5, tx_line['comp_igst'], line_content_style)
                ws1.write(row, col + 6, tx_line['uin_taxable_amt'], line_content_style)
                ws1.write(row, col + 7, tx_line['uin_igst'], line_content_style)

            return row

        # Call the inner functions
        row = prepare_outward_supplies(row)
        row = prepare_eligible_itc(row)
        row = prepare_exempt_supplies(row)
        row = prepare_interest_late_fee(row)
        row = prepare_inter_state_unreg(row)

    """ Utility to get integer present in a string """

    def get_num(self, x):
        return int(''.join(ele for ele in x if ele.isdigit()))

    """ Utility to convert date/datetime to dd/mm/yyyy format """

    def format_date(self, date_in):
        return datetime.strftime(datetime.strptime(date_in, DEFAULT_SERVER_DATE_FORMAT), "%d/%m/%Y")
