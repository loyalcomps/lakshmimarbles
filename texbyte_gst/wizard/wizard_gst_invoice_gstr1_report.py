from odoo import fields, models, api, _

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import float_is_zero, float_compare
import xlwt
import base64
import cStringIO
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

B2CL_INVOICE_AMT_LIMIT = 250000

class GSTInvoiceXLSWizard(models.TransientModel):

    _name = 'texbyte_gst.invoice.report.gstr1.wizard'

    # fields to generate xls
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    inv_type = fields.Selection([('cust_inv','Sales Invoice'),('vndr_bil','Purchase Invoice')],
                                default='cust_inv')

    # fields for download xls
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=128)

    sorted_invoices = []
    refund_invoices = []

    def get_valid_invoices(self):
        # Searching for customer invoices
        from_date = datetime.strptime(self.date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(self.date_to, '%Y-%m-%d').date()
        refund_invoice_ids = []
        if self.inv_type == 'cust_inv':
            inv_domain = ('type', 'in', ('out_invoice', 'out_refund'))
        else:
            inv_domain = ('type', 'in', ('in_invoice', 'in_refund'))

        #Get all invoices including canceled, refund and refunded
        self.all_invoices = self.env['account.invoice'].search([('date_invoice','>=', from_date),('date_invoice','<=', to_date),inv_domain])
        #Canceled invoices
        self.caneceled_invoices = self.all_invoices.filtered(lambda i: i.state == 'cancel')
        #Refund invoices
        self.refund_invoices = self.all_invoices.filtered(lambda i: i.state != 'cancel' and i.refund_invoice_id)  #Skip canceled refunds
        #Refunded invoices
        self.refunded_invoices = self.all_invoices.filtered( lambda i: i.state != 'cancel' and id in self.refund_invoices.mapped('refund_invoice_id').ids )
        #Legitimate invoices -- other than canceled, refund and refunded
        invoices = self.all_invoices.filtered(lambda i: i.id not in self.caneceled_invoices.ids + self.refund_invoices.ids + self.refunded_invoices.ids )
        self.sorted_invoices = invoices.sorted(key=lambda p: (p.date_invoice, p.number))

        #canceled_refund_invoices = []
        #for x in invoice_data:
        #    if x['refund_invoice_id']:
        #        canceled_refund_invoices.append(x)
        #        invoice_data.remove(x)
        #for x in canceled_refund_invoices:
        #    refunded_invoice = (y for y in invoice_data if y['id'] == x['refund_invoice_id'][0]).next() or None
        #    if refunded_invoice:
        #        canceled_refund_invoices.append(refunded_invoice)
        #        invoice_data.remove(refunded_invoice)
        #sorted_invoices = invoice_data.sorted(key=lambda p: (p.date_invoice, p.number))

        #invoice_data = self.env['account.invoice'].search_read([('date_invoice','>=', from_date),('date_invoice','<=', to_date),('refund_invoice_id', '!=', None)])
        #invoice_data = self.env['account.invoice'].search([('date_invoice','>=', from_date),('date_invoice','<=', to_date),('state', '!=', 'cancel'),('refund_invoice_id', '!=', None)])
        ##data with all Refunded invoices
        #for x in invoice_data:
        #    #if x['refund_invoice_id']:
        #    #    refund_invoice_ids.append(x['refund_invoice_id'][0])
        #    refund_invoice_ids.append(x.refund_invoice_id.id)

        ##invoices with filtering with date, non cancelled and not refunded
        #invoices = self.env['account.invoice'].search([('date_invoice','>=', from_date),('date_invoice','<=', to_date), ('state', '!=', 'cancel'), ('refund_invoice_id', '=', None), ('id', 'not in', refund_invoice_ids), inv_domain])
        #return sorted_invoices

    @api.multi
    def generate_gstr1_report(self):
        #Error handling is not taken into consideraion
        self.ensure_one()
        fp = cStringIO.StringIO()
        xl_workbook = xlwt.Workbook(encoding='utf-8')

        from_date = datetime.strptime(self.date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(self.date_to, '%Y-%m-%d').date()

        # Get the invoices
        self.get_valid_invoices()

        self.generate_b2b_report(xl_workbook)
        self.generate_b2ba_report(xl_workbook)
        self.generate_b2cl_report(xl_workbook)
        self.generate_b2cla_report(xl_workbook)
        self.generate_b2cs_report(xl_workbook)
        self.generate_b2csa_report(xl_workbook)
        self.generate_exempted_report(xl_workbook)
        self.generate_cdnr_report(xl_workbook)
        self.generate_cdnra_report(xl_workbook)
        self.generate_cdnur_report(xl_workbook)
        self.generate_at_report(xl_workbook)
        self.generate_ata_report(xl_workbook)
        self.generate_atadj_report(xl_workbook)
        self.generate_atadja_report(xl_workbook)
        self.generate_hsn_report(xl_workbook)
        self.generate_docs_summary_report(xl_workbook)

        xl_workbook.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name':'gstr1_'+str(from_date)+'-'+str(to_date)+'.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'texbyte_gst.invoice.report.gstr1.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    """ B2B (Business to Business report) """
    def generate_b2b_report(self, wb1):
        #Error handling is not taken into consideraion
        self.ensure_one()

        #TODO: format (group & split by tax rate):
        #   GSTIN           Inv No     Inv Date     Inv Value   PoS         Tax Rate    Taxable Value
        #   GSTIN000022     INV001     01/01/2018   5092.00     32-Kerala   5           2200
        #   GSTIN000022     INV001     01/01/2018   5092.00     32-Kerala   12          1600
        #Plan:
        #   1.  Get invoices within range. Filter out 'Canceled', 'Refund' & 'Refunded' invoices
        #   2.  Loop through invoices
        #   3.      Loop through invoice lines
        #   4.          Loop through invoice_line_tax__ids
        #   5.              Collect the invoice, untaxed_total and tax rate/name (such as 'GST @5%')
        #   6.  Loop through collected invoice and tax details
        #   7.      Print invoice details, tax rate/name and untaxed_total

        #wb1 = self.xl_workbook      # xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('b2b')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Invoice information", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "GSTIN/UIN of Recipient", sub_header_style)
        ws1.write(row, col + 2, "Receiver Name", sub_header_style)
        ws1.write(row, col + 3, "Invoice Number", sub_header_style)
        ws1.write(row, col + 4, "Invoice Date", sub_header_style)
        ws1.write(row, col + 5, "Invoice Value", sub_header_style)
        ws1.write(row, col + 6, "Place of Supply", sub_header_style)
        ws1.write(row, col + 7, "Reverse Charge", sub_header_style)
        ws1.write(row, col + 8, "Invoice Type", sub_header_style)
        ws1.write(row, col + 9, "E-Commerce GSTIN", sub_header_style)
        ws1.write(row, col + 10, "Rate", sub_header_style)
        ws1.write(row, col + 11, "Taxable Value", sub_header_style)
        ws1.write(row, col + 12, "Cess Amount", sub_header_style)

        row += 1
        #variables for columns and totals
        igst_amount = 0;
        cgst_amount = 0;
        sgst_amount = 0;

        invoice_gst_tax_lines = {}

        for invoice in self.sorted_invoices.filtered(lambda p: p.partner_id.vat and not p.refund_invoice_id):  #GST registered customers
            #Can't use invoice.tax_line_ids directly because it will contain on individual/leaf taxes (like CGST@2.5%, SGST@2.5%)
            #while GSTR1 report needs the 'group' tax (like GST@5%).
            #Iterate through invoice.invoice_line_ids.invoice_line_tax_line_ids and collect/compute from there
            #for tax_line in invoice.tax_line_ids:
            grouped_tax_lines = {}
            for invoice_line in invoice.invoice_line_ids:
                line_taxes = invoice_line.invoice_line_tax_ids.compute_all(invoice_line.price_unit, invoice.currency_id, invoice_line.quantity, invoice_line.product_id, invoice.partner_id)
                #_logger.info(line_taxes)
                #_logger.info(invoice_line.invoice_line_tax_ids.sorted(reverse=True))
                for ln_tx in invoice_line.invoice_line_tax_ids: #.sorted(reverse=True):
                    gst_tax_id = None
                    if ln_tx.gst_type in ('gst','ugst','igst'):
                        gst_tax_id = ln_tx
                        if grouped_tax_lines.get(ln_tx):
                            grouped_tax_lines[ln_tx][0] += line_taxes['total_excluded']
                        else:
                            grouped_tax_lines[ln_tx] = [0,0]
                            grouped_tax_lines[ln_tx][0] = line_taxes['total_excluded']
                    elif gst_tax_id:       #CESS and other non-GST taxes
                        #TODO:Make the bold assumption that CESS is applied *after* GST taxes, so grouped_tax_lines[gst_tx_id] is already present
                        #if len(grouped_tax_lines.get(ln_tx)) > 1:
                        #Calculate CESS amount only
                        grouped_tax_lines[gst_tax_id][1] += sum(l['amount'] for l in line_taxes['taxes'] if 'GST' not in l['name'])
                        #else:
                        #    grouped_tax_lines[ln_tx][1] = line_taxes['total_excluded']

                #for tax_line in line_taxes['taxes']:
                ##for tax_line in invoce_line.invoice_line_tax_ids:
                #    if grouped_tax_lines.get(tax_line['id']):
                #        grouped_tax_lines[tax_line['id']] += tax_line['base']
                #    else:
                #        grouped_tax_lines[tax_line['id']] = tax_line['base']

            invoice_gst_tax_lines[invoice] = grouped_tax_lines

        for invoice, inv_tax_lines in sorted(invoice_gst_tax_lines.iteritems(), key=lambda p:(p[0].date, p[0].number)): # invoice_gst_tax_lines.items():
            for tax_id, base_amount in inv_tax_lines.items():
                #tax_id = self.env['account.tax'].browse(tax_id_id)
                #if tax_id.gst_type in ('gst','ugst','igst'):
                tax_rate = float( str(tax_id.name).split('@')[1].split('%')[0] )
                if float_is_zero(tax_rate, precision_digits=3):     #Skip zero rated/exempted rates
                    continue
                ws1.write(row, col + 1, invoice.partner_id.vat or "", line_content_style)
                ws1.write(row, col + 2, invoice.partner_id.name, line_content_style)
                ws1.write(row, col + 3, invoice.number, line_content_style)
                ws1.write(row, col + 4, self.format_date(invoice.date_invoice), line_content_style)
                ws1.write(row, col + 5, invoice.amount_total, line_content_style)
                ws1.write(row, col + 6, invoice.place_of_supply.name_get()[0][1], line_content_style)
                ws1.write(row, col + 7, invoice.reverse_charge and "Y" or "N", line_content_style)
                ws1.write(row, col + 8, "Regular", line_content_style)  #TODO: Invoice Type
                ws1.write(row, col + 9, "", line_content_style)         #TODO: E-Commerce GSTIN
                ws1.write(row, col + 11, base_amount[0], line_content_style)
                ws1.write(row, col + 10, tax_rate, line_content_style)
                ws1.write(row, col + 12, base_amount[1], line_content_style)    #Cess amount

                row += 1

        #for invoice in canceled_refund_invoices:
        #    row += 1
        #    ws1.write(row, col + 1, invoice.number, line_content_style)
        #    ws1.write(row, col + 2, invoice.date_invoice, line_content_style)
        #    ws1.write(row, col + 3, invoice.state.title(), line_content_style)
        #    ws1.write(row, col + 4, invoice.origin, line_content_style)
        #    ws1.write(row, col + 5, invoice.partner_id.vat or "", line_content_style)
        #    partner_name = invoice.partner_id.vat and invoice.partner_id.name or invoice.partner_name
        #    ws1.write(row, col + 6, partner_name, line_content_style)

    """ B2BA (Business to Business Amended report) """
    def generate_b2ba_report(self, wb1):
        #Error handling is not taken into consideraion
        self.ensure_one()

        ws1 = wb1.add_sheet('b2ba')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Summary of B2B", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "GSTIN/UIN of Recipient", sub_header_style)
        ws1.write(row, col + 2, "Receiver Name", sub_header_style)
        ws1.write(row, col + 3, "Original Invoice Number", sub_header_style)
        ws1.write(row, col + 4, "Original Invoice Date", sub_header_style)
        ws1.write(row, col + 5, "Revised Invoice Number", sub_header_style)
        ws1.write(row, col + 6, "Revised Invoice Date", sub_header_style)
        ws1.write(row, col + 7, "Invoice Value", sub_header_style)
        ws1.write(row, col + 8, "Place of Supply", sub_header_style)
        ws1.write(row, col + 9, "Reverse Charge", sub_header_style)
        ws1.write(row, col + 10, "Invoice Type", sub_header_style)
        ws1.write(row, col + 11, "E-Commerce GSTIN", sub_header_style)
        ws1.write(row, col + 12, "Rate", sub_header_style)
        ws1.write(row, col + 13, "Taxable Value", sub_header_style)
        ws1.write(row, col + 14, "Cess Amount", sub_header_style)

        row += 1

    """ HSN Summary """
    def generate_hsn_report(self, wb1):
        #Error handling is not taken into consideraion
        self.ensure_one()

        ws1 = wb1.add_sheet('hsn')
        fp = cStringIO.StringIO()

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 12 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 1, 5, "HSN Summary", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "HSN Code", sub_header_style)
        ws1.write(row, col + 2, "Product", sub_header_style)
        ws1.write(row, col + 3, "Unit of Measure", sub_header_style)
        ws1.write(row, col + 4, "Quantity", sub_header_style)
        ws1.write(row, col + 5, "Total Value", sub_header_style)
        ws1.write(row, col + 6, "Taxable Value", sub_header_style)
        ws1.write(row, col + 7, "IGST", sub_header_style)
        ws1.write(row, col + 8, "CGST", sub_header_style)
        ws1.write(row, col + 9, "SGST", sub_header_style)
        ws1.write(row, col + 10, "Cess", sub_header_style)

        hsn_summary_data = {}

        for invoice in self.sorted_invoices:
            for invoice_line in invoice.invoice_line_ids:
                prod_id = invoice_line.product_id
                line_uom = invoice_line.uom_id
                line_qty = line_uom._compute_quantity(invoice_line.quantity, prod_id.uom_id)
                line_amount = invoice_line.price_subtotal_signed
                line_taxes = invoice_line.invoice_line_tax_ids.compute_all(invoice_line.price_unit, invoice_line.invoice_id.currency_id, invoice_line.quantity, prod_id, invoice_line.invoice_id.partner_id)
                #_logger.info(line_taxes)
                igst_amount = cgst_amount = sgst_amount = cess_amount = 0.0
                for tax_line in line_taxes['taxes']:
                    #tax_obj = self.env['account.tax'].browse(tax_line['id'])
                    if 'IGST' in tax_line['name']:   #tax_obj.gst_type == 'igst':
                        igst_amount += tax_line['amount']
                    elif 'CGST' in tax_line['name']: #tax_obj.gst_type == 'cgst':
                        cgst_amount += tax_line['amount']
                    elif 'SGST' in tax_line['name'] or 'UTGST' in tax_line['name']: #tax_obj.gst_type == 'sgst':
                        sgst_amount += tax_line['amount']
                    else:
                        cess_amount += tax_line['amount']

                #cgst_amount = invoice_line.invoice_line_tax_ids.filtered(lambda r: r.gst_type == 'cgst').amount
                #sgst_amount = invoice_line.invoice_line_tax_ids.filtered(lambda r: r.gst_type == 'sgst').amount
                line_total_amount = invoice_line.price_subtotal + igst_amount + cgst_amount + sgst_amount + cess_amount
                #_logger.info(invoice_line.invoice_line_tax_ids)
                if line_amount < 0:
                    line_total_amount = line_total_amount * -1
                if hsn_summary_data.get(prod_id):
                    hsn_summary_data[prod_id][0] += line_qty
                    hsn_summary_data[prod_id][1] += line_total_amount
                    hsn_summary_data[prod_id][2] += line_amount
                    hsn_summary_data[prod_id][3] += igst_amount
                    hsn_summary_data[prod_id][4] += cgst_amount
                    hsn_summary_data[prod_id][5] += sgst_amount
                    hsn_summary_data[prod_id][6] += cess_amount
                else:
                    hsn_summary_data[prod_id] = [line_qty, line_total_amount, line_amount, igst_amount, cgst_amount, sgst_amount, cess_amount]

        #_logger.info(hsn_summary_data)

        #Can't sort dictionary, but get ordered list of tuples
        for product_hsn, hsn_sum in sorted(hsn_summary_data.iteritems(), key=lambda p:p[0].name):
            if product_hsn.default_code in ('ADVANCE','CHARGES','DISCOUNT'):    #Skip Roundoff/Discount/Extra Charges/Advance items
                continue
            row += 1
            ws1.write(row, col + 1, product_hsn.hsncode.hsncode, line_content_style)
            ws1.write(row, col + 2, product_hsn.name, line_content_style)
            ws1.write(row, col + 3, product_hsn.uom_id.name, line_content_style)
            #Quantity in Base UoM
            ws1.write(row, col + 4, hsn_sum[0], line_content_style)
            #Amount
            ws1.write(row, col + 5, hsn_sum[1], line_content_style)
            ws1.write(row, col + 6, hsn_sum[2], line_content_style)
            ws1.write(row, col + 7, hsn_sum[3], line_content_style)
            ws1.write(row, col + 8, hsn_sum[4], line_content_style)
            ws1.write(row, col + 9, hsn_sum[5], line_content_style)
            ws1.write(row, col + 10, hsn_sum[6], line_content_style)

    """ B2CL (Business to Customer Large [>2.5L single invoice] report) """
    def generate_b2cl_report(self, wb1):
        #Error handling is not taken into consideraion
        self.ensure_one()

        #TODO: format (group & split by tax rate):
        #   GSTIN           Inv No     Inv Date     Inv Value   PoS         Tax Rate    Taxable Value
        #   GSTIN000022     INV001     01/01/2018   5092.00     32-Kerala   5           2200
        #   GSTIN000022     INV001     01/01/2018   5092.00     32-Kerala   12          1600
        #Plan:
        #   1.  Get invoices within range. Filter out 'Canceled', 'Refund' & 'Refunded' invoices
        #   2.  Loop through invoices
        #   3.      Loop through invoice lines
        #   4.          Loop through invoice_line_tax__ids
        #   5.              Collect the invoice, untaxed_total and tax rate/name (such as 'GST @5%')
        #   6.  Loop through collected invoice and tax details
        #   7.      Print invoice details, tax rate/name and untaxed_total

        #wb1 = self.xl_workbook      # xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('b2cl')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "B2CL Invoices", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Invoice Number", sub_header_style)
        ws1.write(row, col + 2, "Invoice Date", sub_header_style)
        ws1.write(row, col + 3, "Invoice Value", sub_header_style)
        ws1.write(row, col + 4, "Place of Supply", sub_header_style)
        ws1.write(row, col + 5, "Rate", sub_header_style)
        ws1.write(row, col + 6, "Taxable Value", sub_header_style)
        ws1.write(row, col + 7, "Cess Amount", sub_header_style)
        ws1.write(row, col + 8, "E-Commerce GSTIN", sub_header_style)

        row += 1
        #variables for columns and totals

        invoice_gst_tax_lines = {}

        for invoice in self.sorted_invoices.filtered(lambda p: not p.partner_id.vat and p.company_id.place_of_supply != p.place_of_supply \
                                                               and p.amount_untaxed_signed > B2CL_INVOICE_AMT_LIMIT and not p.refund_invoice_id):  #Unregistered large sale
            #Can't use invoice.tax_line_ids directly because it will contain on individual/leaf taxes (like CGST@2.5%, SGST@2.5%)
            #while GSTR1 report needs the 'group' tax (like GST@5%).
            #Iterate through invoice.invoice_line_ids.invoice_line_tax_line_ids and collect/compute from there
            #for tax_line in invoice.tax_line_ids:
            grouped_tax_lines = {}
            for invoice_line in invoice.invoice_line_ids:
                line_taxes = invoice_line.invoice_line_tax_ids.compute_all(invoice_line.price_unit, invoice.currency_id, invoice_line.quantity, invoice_line.product_id, invoice.partner_id)
                #_logger.info(line_taxes)
                for ln_tx in invoice_line.invoice_line_tax_ids:
                    gst_tax_id = None
                    if ln_tx.gst_type in ('gst','ugst','igst'):
                        gst_tax_id = ln_tx
                        if grouped_tax_lines.get(ln_tx):
                            grouped_tax_lines[ln_tx][0] += line_taxes['total_excluded']
                        else:
                            grouped_tax_lines[ln_tx] = [0,0]
                            grouped_tax_lines[ln_tx][0] = line_taxes['total_excluded']
                    elif gst_tax_id:       #CESS and other non-GST taxes
                        #Calculate CESS amount only
                        grouped_tax_lines[gst_tax_id][1] += sum(l['amount'] for l in line_taxes['taxes'] if 'GST' not in l['name'])

                #for tax_line in line_taxes['taxes']:
                ##for tax_line in invoce_line.invoice_line_tax_ids:
                #    if grouped_tax_lines.get(tax_line['id']):
                #        grouped_tax_lines[tax_line['id']] += tax_line['base']
                #    else:
                #        grouped_tax_lines[tax_line['id']] = tax_line['base']

            invoice_gst_tax_lines[invoice] = grouped_tax_lines

        for invoice, inv_tax_lines in sorted(invoice_gst_tax_lines.iteritems(), key=lambda p:(p[0].date, p[0].number)): # invoice_gst_tax_lines.items():
            for tax_id, base_amount in inv_tax_lines.items():
                #tax_id = self.env['account.tax'].browse(tax_id_id)
                tax_rate = float( str(tax_id.name).split('@')[1].split('%')[0] )
                if float_is_zero(tax_rate, precision_digits=3):     #Skip zero rated/exempted rates
                    continue
                ws1.write(row, col + 1, invoice.number, line_content_style)
                ws1.write(row, col + 2, self.format_date(invoice.date_invoice), line_content_style)
                ws1.write(row, col + 3, invoice.amount_total, line_content_style)
                ws1.write(row, col + 4, invoice.place_of_supply.name_get()[0][1], line_content_style)
                ws1.write(row, col + 5, tax_rate, line_content_style)
                ws1.write(row, col + 6, base_amount[0], line_content_style)
                ws1.write(row, col + 7, base_amount[1], line_content_style) #Cess amount
                ws1.write(row, col + 8, "", line_content_style)             #TODO: E-Commerce GSTIN

                row += 1

    """ B2CLA (Business to Customer Large Amended [>2.5L single invoice] report) """
    def generate_b2cla_report(self, wb1):
        #Error handling is not taken into consideraion
        self.ensure_one()

        ws1 = wb1.add_sheet('b2cla')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "B2CLA Invoices", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Original Invoice Number", sub_header_style)
        ws1.write(row, col + 2, "Original Invoice Date", sub_header_style)
        ws1.write(row, col + 3, "Original Place of Supply", sub_header_style)
        ws1.write(row, col + 4, "Revised Invoice Number", sub_header_style)
        ws1.write(row, col + 5, "Revised Invoice Date", sub_header_style)
        ws1.write(row, col + 6, "Invoice Value", sub_header_style)
        ws1.write(row, col + 7, "Rate", sub_header_style)
        ws1.write(row, col + 8, "Taxable Value", sub_header_style)
        ws1.write(row, col + 9, "Cess Amount", sub_header_style)
        ws1.write(row, col + 10, "E-Commerce GSTIN", sub_header_style)

        row += 1

    """ B2CS (Business to Customer Small) report """
    def generate_b2cs_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('b2cs')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "B2CS Invoice Details", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Invoice Type", sub_header_style)
        ws1.write(row, col + 2, "Place of Supply", sub_header_style)
        ws1.write(row, col + 3, "Rate", sub_header_style)
        ws1.write(row, col + 4, "Taxable Value", sub_header_style)
        ws1.write(row, col + 5, "Cess Amount", sub_header_style)
        ws1.write(row, col + 6, "E-Commerce GSTIN", sub_header_style)

        row += 1

        invoice_pos_tax_lines = {}

        for invoice in self.sorted_invoices.filtered(lambda p: not p.partner_id.vat and not p.refund_invoice_id and not \
                                                                (p.company_id.place_of_supply != p.place_of_supply and p.amount_untaxed_signed > B2CL_INVOICE_AMT_LIMIT)):  #Unregistered customer sale other than B2CL
            #Can't use invoice.tax_line_ids directly because it will contain on individual/leaf taxes (like CGST@2.5%, SGST@2.5%)
            #while GSTR1 report needs the 'group' tax (like GST@5%).
            #Iterate through invoice.invoice_line_ids.invoice_line_tax_line_ids and collect/compute from there
            PoS = invoice.place_of_supply
            for invoice_line in invoice.invoice_line_ids:
                #TODO: handle CESS also here
                line_taxes = invoice_line.invoice_line_tax_ids.compute_all(invoice_line.price_unit, invoice.currency_id, invoice_line.quantity, invoice_line.product_id, invoice.partner_id)
                #_logger.info(line_taxes)
                for ln_tx in invoice_line.invoice_line_tax_ids:
                    gst_tax_id = None
                    if ln_tx.gst_type in ('gst','ugst','igst'):
                        gst_tax_id = ln_tx
                        if invoice_pos_tax_lines.get(PoS):
                            if invoice_pos_tax_lines[PoS].get(ln_tx):
                                invoice_pos_tax_lines[PoS][ln_tx][0] += line_taxes['total_excluded']
                            else:
                                invoice_pos_tax_lines[PoS][ln_tx] = [0,0]
                                invoice_pos_tax_lines[PoS][ln_tx][0] = line_taxes['total_excluded']
                        else:
                            invoice_pos_tax_lines[PoS] = {ln_tx: [line_taxes['total_excluded'],0]}
                    elif gst_tax_id:       #CESS and other taxes, added to the previous GST rate
                        #if invoice_pos_tax_lines[PoS].get(ln_tx):
                        invoice_pos_tax_lines[PoS][gst_tax_id][1] += sum(l['amount'] for l in line_taxes['taxes'] if 'GST' not in l['name'])
                        #else:
                        #    invoice_pos_tax_lines[PoS][ln_tx] = 0


        for place_of_supply, inv_tax_lines in invoice_pos_tax_lines.items():
            for tax_id, base_amount in inv_tax_lines.items():
                #tax_id = self.env['account.tax'].browse(tax_id_id)
                tax_rate = float( str(tax_id.name).split('@')[1].split('%')[0] )
                if float_is_zero(tax_rate, precision_digits=3):     #Skip zero rated/exempted rates
                    continue
                ws1.write(row, col + 1, "OE", line_content_style)       #TODO: 'OE'
                ws1.write(row, col + 2, place_of_supply.name_get()[0][1], line_content_style)
                ws1.write(row, col + 3, tax_rate, line_content_style)
                ws1.write(row, col + 4, base_amount[0], line_content_style)
                ws1.write(row, col + 5, base_amount[1], line_content_style) # Cess amount
                ws1.write(row, col + 6, "", line_content_style)     #TODO: E-Commerce GSTIN

                row += 1

    """ B2CSA (Business to Customer Small Amended) report """
    def generate_b2csa_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('b2csa')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "B2CSA Invoice Details", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Financial Year", sub_header_style)
        ws1.write(row, col + 2, "Original Month", sub_header_style)
        ws1.write(row, col + 3, "Original Place of Supply", sub_header_style)
        ws1.write(row, col + 4, "Revised Place of Supply", sub_header_style)
        ws1.write(row, col + 5, "Invoice Type", sub_header_style)
        ws1.write(row, col + 6, "Rate", sub_header_style)
        ws1.write(row, col + 7, "Taxable Value", sub_header_style)
        ws1.write(row, col + 8, "Cess Amount", sub_header_style)
        ws1.write(row, col + 9, "E-Commerce GSTIN", sub_header_style)

        row += 1

    """ Exempted (Nil Rated, Exempted and Non GST supplies) report """
    def generate_exempted_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('exemp')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Summary For Nil rated, exempted and non GST outward supplies (8)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Description", sub_header_style)
        ws1.write(row, col + 2, "Nil Rated Supplies", sub_header_style)
        ws1.write(row, col + 3, "Exmempted (other than nil rated/non GST)", sub_header_style)
        ws1.write(row, col + 4, "Non-GST Supplies", sub_header_style)

        row += 1

        nil_rated_idx = 0
        exempted_idx  = 1
        non_gst_idx   = 2
        gst_exempted_values = { 'reg':{'inter-state':[0.0, 0.0, 0.0], 'intra-state':[0.0, 0.0, 0.0]}, 'unreg':{'inter-state':[0.0, 0.0, 0.0], 'intra-state':[0.0, 0.0, 0.0]} }
        for invoice in self.sorted_invoices:
            for invoice_line in invoice.invoice_line_ids.filtered(lambda l: l.product_id.default_code not in ('ADVANCE','CHARGES','DISCOUNT')):
                taxes = invoice_line.invoice_line_tax_ids.compute_all(invoice_line.price_unit, invoice.currency_id, invoice_line.quantity, invoice_line.product_id, invoice.partner_id)
                if float_compare(taxes['total_included'], taxes['total_excluded'], precision_digits=3) == 0:  #TODO: use float_compare
                    #TODO: separate Nil-Rated, Exempted & Non-GST ones
                    #TODO: Assume there will be only 1 tax in the case of Zero tax
                    if taxes['taxes'] and 'GST' in taxes['taxes'][0]['name']:     #TODO: handle non-GST
                        l_index = nil_rated_idx
                    else:
                        l_index = exempted_idx

                    if invoice.partner_id.vat:
                        if invoice.place_of_supply == invoice.company_id.place_of_supply:
                            gst_exempted_values['reg']['intra-state'][l_index] += invoice_line.price_subtotal_signed
                        else:
                            gst_exempted_values['reg']['inter-state'][l_index] += invoice_line.price_subtotal_signed
                    else:
                        if invoice.place_of_supply == invoice.company_id.place_of_supply:
                            gst_exempted_values['unreg']['intra-state'][l_index] += invoice_line.price_subtotal_signed
                        else:
                            gst_exempted_values['unreg']['inter-state'][l_index] += invoice_line.price_subtotal_signed

        for exemp_key, exemp_val in gst_exempted_values.items():
            if exemp_key == 'reg':
                ws1.write(row, col+1, 'Inter-State supplies to registered persons')
                ws1.write(row, col+2, exemp_val['inter-state'][0])
                ws1.write(row, col+3, exemp_val['inter-state'][1])
                ws1.write(row, col+4, exemp_val['inter-state'][2])
                row += 1
                ws1.write(row, col+1, 'Intra-State supplies to registered persons')
                ws1.write(row, col+2, exemp_val['intra-state'][0])
                ws1.write(row, col+3, exemp_val['intra-state'][1])
                ws1.write(row, col+4, exemp_val['intra-state'][2])
            else:
                ws1.write(row, col+1, 'Inter-State supplies to unregistered persons')
                ws1.write(row, col+2, exemp_val['inter-state'][0])
                ws1.write(row, col+3, exemp_val['inter-state'][1])
                ws1.write(row, col+4, exemp_val['inter-state'][2])
                row += 1
                ws1.write(row, col+1, 'Intra-State supplies to unregistered persons')
                ws1.write(row, col+2, exemp_val['intra-state'][0])
                ws1.write(row, col+3, exemp_val['intra-state'][1])
                ws1.write(row, col+4, exemp_val['intra-state'][2])

            row += 1

    """ CDNR (Credit/Debit Note Registered) """
    def generate_cdnr_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('cdnr')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Credit / Debit Note Registered Details", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "GSTIN/UIN of Recipient", sub_header_style)
        ws1.write(row, col + 2, "Receiver Name", sub_header_style)
        ws1.write(row, col + 3, "Invoice/Advance Receipt Number", sub_header_style)
        ws1.write(row, col + 4, "Invoice/Advance Receipt date", sub_header_style)
        ws1.write(row, col + 5, "Note/Refund Voucher Number", sub_header_style)
        ws1.write(row, col + 6, "Note/Refund Voucher date", sub_header_style)
        ws1.write(row, col + 7, "Document Type", sub_header_style)
        ws1.write(row, col + 8, "Reason For Issuing document", sub_header_style)
        ws1.write(row, col + 9, "Place Of Supply", sub_header_style)
        ws1.write(row, col + 10, "Note/Refund Voucher Value", sub_header_style)
        ws1.write(row, col + 11, "Rate", sub_header_style)
        ws1.write(row, col + 12, "Taxable Value", sub_header_style)
        ws1.write(row, col + 13, "Cess Amount", sub_header_style)
        ws1.write(row, col + 14, "Pre GST", sub_header_style)

        row += 1

        invoice_gst_tax_lines = {}

        for invoice in self.refund_invoices.filtered(lambda p: p.partner_id.vat and \
                                                        p.type in ('in_refund','out_refund')): #GST registered customers
            #Can't use invoice.tax_line_ids directly because it will contain on individual/leaf taxes (like CGST@2.5%, SGST@2.5%)
            #while GSTR1 report needs the 'group' tax (like GST@5%).
            #Iterate through invoice.invoice_line_ids.invoice_line_tax_line_ids and collect/compute from there
            #for tax_line in invoice.tax_line_ids:
            grouped_tax_lines = {}
            for invoice_line in invoice.invoice_line_ids:
                line_taxes = invoice_line.invoice_line_tax_ids.compute_all(invoice_line.price_unit, invoice.currency_id, invoice_line.quantity, invoice_line.product_id, invoice.partner_id)
                #_logger.info(line_taxes)
                #_logger.info(invoice_line.invoice_line_tax_ids.sorted(reverse=True))
                for ln_tx in invoice_line.invoice_line_tax_ids: #.sorted(reverse=True):
                    gst_tax_id = None
                    if ln_tx.gst_type in ('gst','ugst','igst'):
                        gst_tax_id = ln_tx
                        if grouped_tax_lines.get(ln_tx):
                            grouped_tax_lines[ln_tx][0] += line_taxes['total_excluded']
                        else:
                            grouped_tax_lines[ln_tx] = [0,0]
                            grouped_tax_lines[ln_tx][0] = line_taxes['total_excluded']
                    elif gst_tax_id:       #CESS and other non-GST taxes
                        #TODO:Make the bold assumption that CESS is applied *after* GST taxes, so grouped_tax_lines[gst_tx_id] is already present
                        #Calculate CESS amount only
                        grouped_tax_lines[gst_tax_id][1] += sum(l['amount'] for l in line_taxes['taxes'] if 'GST' not in l['name'])

            invoice_gst_tax_lines[invoice] = grouped_tax_lines


        for invoice, inv_tax_lines in sorted(invoice_gst_tax_lines.iteritems(), key=lambda p:(p[0].date, p[0].number)): # invoice_gst_tax_lines.items():
            for tax_id, base_amount in inv_tax_lines.items():
                #tax_id = self.env['account.tax'].browse(tax_id_id)
                tax_rate = float( str(tax_id.name).split('@')[1].split('%')[0] )
                ws1.write(row, col + 1, invoice.partner_id.vat, line_content_style)
                ws1.write(row, col + 2, invoice.partner_id.name, line_content_style)
                ws1.write(row, col + 3, invoice.refund_invoice_id.number, line_content_style)
                ws1.write(row, col + 4, self.format_date(invoice.refund_invoice_id.date_invoice), line_content_style)
                ws1.write(row, col + 5, invoice.number, line_content_style)
                ws1.write(row, col + 6, self.format_date(invoice.date_invoice), line_content_style)
                ws1.write(row, col + 7, invoice.type == 'in_refund' and "D" or "C", line_content_style)
                ws1.write(row, col + 8, invoice.name, line_content_style)
                ws1.write(row, col + 9, invoice.place_of_supply.name_get()[0][1], line_content_style)
                ws1.write(row, col + 10,invoice.amount_total, line_content_style)
                ws1.write(row, col + 11, tax_rate, line_content_style)
                ws1.write(row, col + 12, base_amount[0], line_content_style)
                ws1.write(row, col + 13, base_amount[1], line_content_style)
                ws1.write(row, col + 14, " ", line_content_style)

                row += 1

    """ CDNRA (Amended Credit/Debit Note) """
    def generate_cdnra_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('cdnra')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Amended Credit / Debit Note ", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "GSTIN/UIN of Recipient", sub_header_style)
        ws1.write(row, col + 2, "Name of Recipient", sub_header_style)
        ws1.write(row, col + 3, "Original Invoice/Advance Receipt Number", sub_header_style)
        ws1.write(row, col + 4, "Original Invoice/Advance Receipt date", sub_header_style)
        ws1.write(row, col + 5, "Original Note/ Refund Voucher Number", sub_header_style)
        ws1.write(row, col + 6, "Original Note/ Refund Voucher date", sub_header_style)
        ws1.write(row, col + 7, "Revised Note/Refund Voucher Number", sub_header_style)
        ws1.write(row, col + 8, "Revised Note/Refund Voucher date", sub_header_style)
        ws1.write(row, col + 9, "Document Type", sub_header_style)
        ws1.write(row, col + 10, "Reason For Issuing document", sub_header_style)
        ws1.write(row, col + 11, "Place Of Supply", sub_header_style)
        ws1.write(row, col + 12, "Note/Refund Voucher Value", sub_header_style)
        ws1.write(row, col + 13, "Rate", sub_header_style)
        ws1.write(row, col + 14, "Taxable Value", sub_header_style)
        ws1.write(row, col + 15, "Cess Amount", sub_header_style)
        ws1.write(row, col + 16, "Pre GST", sub_header_style)

        row += 1

    """ CDNUR (Credit/Debit Note Unregistered, more than 2.5 lakh) """
    def generate_cdnur_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('cdnur')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Credit/Debit Note Unregistered Details", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "UR Type", sub_header_style)
        ws1.write(row, col + 2, "Note/Refund Voucher Number", sub_header_style)
        ws1.write(row, col + 3, "Note/Refund Voucher date", sub_header_style)
        ws1.write(row, col + 4, "Document Type", sub_header_style)
        ws1.write(row, col + 5, "Invoice/Advance Receipt Number", sub_header_style)
        ws1.write(row, col + 6, "Invoice/Advance Receipt Date", sub_header_style)
        ws1.write(row, col + 7, "Reason For Issuing document", sub_header_style)
        ws1.write(row, col + 8, "Place Of Supply", sub_header_style)
        ws1.write(row, col + 9, "Note/Refund Voucher Value", sub_header_style)
        ws1.write(row, col + 10, "Rate", sub_header_style)
        ws1.write(row, col + 11, "Taxable Value", sub_header_style)
        ws1.write(row, col + 12, "Cess Amount", sub_header_style)
        ws1.write(row, col + 13, "Pre GST", sub_header_style)

        row += 1

        invoice_gst_tax_lines = {}

        for invoice in self.refund_invoices.filtered(lambda p: not p.partner_id.vat and p.company_id.place_of_supply != p.place_of_supply \
                                                     and (p.amount_untaxed_signed * -1) > B2CL_INVOICE_AMT_LIMIT and p.type in ('in_refund', 'out_refund')):
            #Can't use invoice.tax_line_ids directly because it will contain on individual/leaf taxes (like CGST@2.5%, SGST@2.5%)
            #while GSTR1 report needs the 'group' tax (like GST@5%).
            #Iterate through invoice.invoice_line_ids.invoice_line_tax_line_ids and collect/compute from there
            #for tax_line in invoice.tax_line_ids:
            _logger.info(invoice)
            grouped_tax_lines = {}
            for invoice_line in invoice.invoice_line_ids:
                line_taxes = invoice_line.invoice_line_tax_ids.compute_all(invoice_line.price_unit, invoice.currency_id, invoice_line.quantity, invoice_line.product_id, invoice.partner_id)
                #_logger.info(line_taxes)
                #_logger.info(invoice_line.invoice_line_tax_ids.sorted(reverse=True))
                for ln_tx in invoice_line.invoice_line_tax_ids: #.sorted(reverse=True):
                    gst_tax_id = None
                    if ln_tx.gst_type in ('gst','ugst','igst'):
                        gst_tax_id = ln_tx
                        if grouped_tax_lines.get(ln_tx):
                            grouped_tax_lines[ln_tx][0] += line_taxes['total_excluded']
                        else:
                            grouped_tax_lines[ln_tx] = [0,0]
                            grouped_tax_lines[ln_tx][0] = line_taxes['total_excluded']
                    elif gst_tax_id:       #CESS and other non-GST taxes
                        #TODO:Make the bold assumption that CESS is applied *after* GST taxes, so grouped_tax_lines[gst_tx_id] is already present
                        #Calculate CESS amount only
                        grouped_tax_lines[gst_tax_id][1] += sum(l['amount'] for l in line_taxes['taxes'] if 'GST' not in l['name'])

            invoice_gst_tax_lines[invoice] = grouped_tax_lines
            #_logger.info(grouped_tax_lines)


        for invoice, inv_tax_lines in sorted(invoice_gst_tax_lines.iteritems(), key=lambda p:(p[0].date, p[0].number)): # invoice_gst_tax_lines.items():
            for tax_id, base_amount in inv_tax_lines.items():
                #tax_id = self.env['account.tax'].browse(tax_id_id)
                tax_rate = float( str(tax_id.name).split('@')[1].split('%')[0] )
                ws1.write(row, col + 1, 'B2CL', line_content_style)
                ws1.write(row, col + 2, invoice.number, line_content_style)
                ws1.write(row, col + 3, self.format_date(invoice.date_invoice), line_content_style)
                ws1.write(row, col + 4, invoice.type == 'in_refund' and "D" or "C", line_content_style)
                ws1.write(row, col + 5, invoice.refund_invoice_id.number, line_content_style)
                ws1.write(row, col + 6, self.format_date(invoice.refund_invoice_id.date_invoice), line_content_style)
                ws1.write(row, col + 7, invoice.name, line_content_style)
                ws1.write(row, col + 8, invoice.place_of_supply.name_get()[0][1], line_content_style)
                ws1.write(row, col + 9, invoice.amount_total, line_content_style)
                ws1.write(row, col + 10, tax_rate, line_content_style)
                ws1.write(row, col + 11, base_amount[0], line_content_style)
                ws1.write(row, col + 12, base_amount[1], line_content_style)
                ws1.write(row, col + 13, " ", line_content_style)

                row += 1

    """ AT (Tax on Advance) report """
    def generate_at_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('at')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Summary For Advance Received (11B)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Place Of Supply", sub_header_style)
        ws1.write(row, col + 2, "Rate", sub_header_style)
        ws1.write(row, col + 3, "Gross Advance Received", sub_header_style)
        ws1.write(row, col + 4, "Cess Amount", sub_header_style)

        row += 1

    """ ATA (Amended Tax on Advance) report """
    def generate_ata_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('ata')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Summary For Amended Tax Liability (Advance Received)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Financial Year", sub_header_style)
        ws1.write(row, col + 2, "Original Month", sub_header_style)
        ws1.write(row, col + 3, "Original Place of Supply", sub_header_style)
        ws1.write(row, col + 4, "Rate", sub_header_style)
        ws1.write(row, col + 5, "Gross Advance Received", sub_header_style)
        ws1.write(row, col + 6, "Cess Amount", sub_header_style)

        row += 1

    """ ATADJ (Advance adjustments) report """
    def generate_atadj_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('atadj')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Summary For Advance Adjusted (11B)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Place Of Supply", sub_header_style)
        ws1.write(row, col + 2, "Rate", sub_header_style)
        ws1.write(row, col + 3, "Gross Advance Adjusted", sub_header_style)
        ws1.write(row, col + 4, "Cess Amount", sub_header_style)

        row += 1

    """ ATA (Amended Tax on Advance) report """
    def generate_atadja_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('atadja')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Summary For Amendement Of Adjustment Advances", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Financial Year", sub_header_style)
        ws1.write(row, col + 2, "Original Month", sub_header_style)
        ws1.write(row, col + 3, "Original Place of Supply", sub_header_style)
        ws1.write(row, col + 4, "Rate", sub_header_style)
        ws1.write(row, col + 5, "Gross Advance Received", sub_header_style)
        ws1.write(row, col + 6, "Cess Amount", sub_header_style)

        row += 1

    """ Docs (Summary of Documents) """
    def generate_docs_summary_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('docs')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Summary of documents issued", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Nature of Document", sub_header_style)
        ws1.write(row, col + 2, "Sr. No. From", sub_header_style)
        ws1.write(row, col + 3, "Sr. No. To", sub_header_style)
        ws1.write(row, col + 4, "Total Number", sub_header_style)
        ws1.write(row, col + 5, "Canceled", sub_header_style)

        row += 1
        sorted_invs = self.all_invoices.sorted(key=lambda p: p.number)
        if not sorted_invs:
            return

        ws1.write(row, col + 1, "Invoices for outward supply")
        ws1.write(row, col + 2, sorted_invs[0].number)
        ws1.write(row, col + 3, sorted_invs[-1].number)
        ws1.write(row, col + 4, len(sorted_invs))
        ws1.write(row, col + 5, len(self.caneceled_invoices)) #+ len(self.refund_invoices) + len(self.refunded_invoices))

    """ Utility to get integer present in a string """
    def get_num(self, x):
        return int(''.join(ele for ele in x if ele.isdigit()))

    """ Utility to convert date/datetime to dd/mm/yyyy format """
    def format_date(self, date_in):
        return datetime.strftime(datetime.strptime(date_in, DEFAULT_SERVER_DATE_FORMAT), "%d/%m/%Y")
