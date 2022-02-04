from odoo import fields, models, api, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import xlwt
import base64
import cStringIO
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

B2CL_INVOICE_AMT_LIMIT = 250000

class TeXByteGSTGSTR2Wizard(models.TransientModel):


    _name = 'invoice.report.gstr2.wizard'

    # fields to generate xls
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    inv_type = fields.Selection([('cust_inv','Sales Invoice'),('vndr_bil','Purchase Invoice')],
                                default='vndr_bil')

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
        self.refund_invoices = self.all_invoices.filtered(lambda i: i.state not in ('cancel','draft') and i.refund_invoice_id)  #Skip canceled refunds
        #Refunded invoices
        self.refunded_invoices = self.all_invoices.filtered( lambda i: i.state != 'cancel' and id in self.refund_invoices.mapped('refund_invoice_id').ids )
        #Legitimate invoices -- other than canceled, refund and refunded
        invoices = self.all_invoices.filtered(lambda i: i.id not in self.caneceled_invoices.ids + self.refund_invoices.ids + self.refunded_invoices.ids )
        self.sorted_invoices = invoices.sorted(key=lambda p: (p.date_invoice, p.number))


    @api.multi
    def generate_gstr2_report(self):
        #Error handling is not taken into consideraion
        self.ensure_one()
        fp = cStringIO.StringIO()
        xl_workbook = xlwt.Workbook(encoding='utf-8')

        from_date = datetime.strptime(self.date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(self.date_to, '%Y-%m-%d').date()

        # Get the invoices
        self.get_valid_invoices()

        # self.generate_b2b_report(xl_workbook)
        # self.generate_b2bur_report(xl_workbook)
        # self.generate_imps_report(xl_workbook)
        # self.generate_impg_report(xl_workbook)
        self.generate_cdnr_report(xl_workbook)
        self.generate_cdnur_report(xl_workbook)
        # self.generate_at_report(xl_workbook)
        # self.generate_atadj_report(xl_workbook)
        # self.generate_exempted_report(xl_workbook)
        # self.generate_itcr_report(xl_workbook)
        # self.generate_hsn_report(xl_workbook)


        xl_workbook.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name':'gstr2_'+str(from_date)+'-'+str(to_date)+'.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.report.gstr2.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }



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
        ws1.write_merge(row, row, 2, 6, "Summary For CDNR(6C)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "GSTIN of Supplier", sub_header_style)
        ws1.write(row, col + 2, "Note/Refund Voucher Number", sub_header_style)
        ws1.write(row, col + 3, "Note/Refund Voucher date", sub_header_style)
        ws1.write(row, col + 4, "Invoice/Advance Payment Voucher Number", sub_header_style)
        ws1.write(row, col + 5, "Invoice/Advance Payment Voucher date", sub_header_style)
        ws1.write(row, col + 6, "Pre GST", sub_header_style)
        ws1.write(row, col + 7, "Document Type", sub_header_style)
        ws1.write(row, col + 8, "Reason For Issuing document", sub_header_style)
        ws1.write(row, col + 9, "Supply Type", sub_header_style)
        ws1.write(row, col + 10, "Note/Refund Voucher Value", sub_header_style)
        ws1.write(row, col + 11, "Rate", sub_header_style)
        ws1.write(row, col + 12, "Taxable Value", sub_header_style)
        ws1.write(row, col + 13, "Integrated Tax Paid", sub_header_style)
        ws1.write(row, col + 14, "Central Tax Paid", sub_header_style)
        ws1.write(row, col + 15, "State/UT Tax Paid", sub_header_style)
        ws1.write(row, col + 16, "Cess Paid", sub_header_style)
        ws1.write(row, col + 17, "Eligibility For ITC", sub_header_style)
        ws1.write(row, col + 18, "Availed ITC Integrated Tax", sub_header_style)
        ws1.write(row, col + 19, "Availed ITC Central Tax", sub_header_style)
        ws1.write(row, col + 20, "Availed ITC State/UT Tax", sub_header_style)
        ws1.write(row, col + 21, "Availed ITC Cess", sub_header_style)


        row += 1

        invoice_gst_tax_lines = {}

        for invoice in self.refund_invoices.filtered(lambda p: p.partner_id.x_gstin and \
                                                        p.type in ('in_refund','out_refund')): #GST registered customers
            #Can't use invoice.tax_line_ids directly because it will contain on individual/leaf taxes (like CGST@2.5%, SGST@2.5%)
            #while gstr2 report needs the 'group' tax (like GST@5%).
            #Iterate through invoice.invoice_line_ids.invoice_line_tax_line_ids and collect/compute from there
            #for tax_line in invoice.tax_line_ids:
            grouped_tax_lines = {}
            for invoice_line in invoice.invoice_line_ids:
                if invoice_line.discount_amount and invoice_line.quantity != 0:
                    price = invoice_line.price_unit - (invoice_line.discount_amount / invoice_line.quantity)
                elif invoice_line.discount:
                    price = invoice_line.price_unit * (1 - (invoice_line.discount or 0.0) / 100.0)
                else:
                    price = invoice_line.price_unit

                if invoice_line.invoice_id.inclusive:
                    line_taxes = invoice_line.invoice_line_tax_ids.with_context(price_include=True,
                                                                   include_base_amount=True).compute_all_inc(price,
                                                                                                             invoice.currency_id,
                                                                                                             invoice_line.quantity,
                                                                                                             product=invoice_line.product_id,
                                                                                                             partner=invoice.partner_id)
                else:
                    line_taxes = invoice_line.invoice_line_tax_ids.compute_all(price,
                                                                               invoice.currency_id,
                                                                           invoice_line.quantity, invoice_line.product_id,
                                                                               invoice.partner_id)
                # line_taxes = invoice_line.invoice_line_tax_ids.compute_all(price, invoice.currency_id, invoice_line.quantity, invoice_line.product_id, invoice.partner_id)

                #_logger.info(line_taxes)
                #_logger.info(invoice_line.invoice_line_tax_ids.sorted(reverse=True))
                for ln_tx in invoice_line.invoice_line_tax_ids: #.sorted(reverse=True):
                    gst_tax_id = None
                    gst_tax_id = ln_tx
                    if grouped_tax_lines.get(ln_tx):
                        grouped_tax_lines[ln_tx][0] += line_taxes['total_excluded']
                    else:
                        grouped_tax_lines[ln_tx] = [0,0,0,0,0]  #[Taxable amount, Cess amount, IGST, CGST, SGST]
                        grouped_tax_lines[ln_tx][0] = line_taxes['total_excluded']
                    for tax_line in line_taxes['taxes']:
                        if 'IGST' in tax_line['name']:
                            grouped_tax_lines[ln_tx][2] += tax_line['amount']
                        elif 'CGST' in tax_line['name']:
                            grouped_tax_lines[ln_tx][3] += tax_line['amount']
                        elif 'SGST' in tax_line['name'] or 'UTGST' in tax_line['name']:
                            grouped_tax_lines[ln_tx][4] += tax_line['amount']

                        else :       #CESS and other non-GST taxes
                            #TODO:Make the bold assumption that CESS is applied *after* GST taxes, so grouped_tax_lines[gst_tx_id] is already present
                            #Calculate CESS amount only
                            grouped_tax_lines[gst_tax_id][1] += sum(l['amount'] for l in line_taxes['taxes'] if 'GST' not in l['name'])

            invoice_gst_tax_lines[invoice] = grouped_tax_lines


        for invoice, inv_tax_lines in sorted(invoice_gst_tax_lines.iteritems(), key=lambda p:(p[0].date, p[0].number)): # invoice_gst_tax_lines.items():
            for tax_id, base_amount in inv_tax_lines.items():
                #tax_id = self.env['account.tax'].browse(tax_id_id)
                for rateObj in tax_id:
                    if rateObj.amount_type == "group":
                        for childObj in rateObj.children_tax_ids:
                            tax_rate = childObj.amount * 2
                            break
                    else:
                        tax_rate = rateObj.amount

                    break
                # tax_rate = float( str(tax_id.name).split('@')[1].split('%')[0] )
                # if float_is_zero(tax_rate, precision_digits=3):     #Skip zero rated/exempted rates
                #     continue
                ws1.write(row, col + 1, invoice.partner_id.x_gstin, line_content_style)
                ws1.write(row, col + 2, invoice.number, line_content_style)
                ws1.write(row, col + 3, self.format_date(invoice.date_invoice), line_content_style)
                ws1.write(row, col + 4, invoice.refund_invoice_id.number, line_content_style)
                ws1.write(row, col + 5, self.format_date(invoice.refund_invoice_id.date_invoice), line_content_style)
                ws1.write(row, col + 6, "", line_content_style)
                ws1.write(row, col + 7, invoice.type == 'in_refund' and "D" or "C", line_content_style)
                ws1.write(row, col + 8, invoice.name, line_content_style)
                ws1.write(row, col + 9, "", line_content_style)
                ws1.write(row, col + 10,invoice.amount_total, line_content_style)
                ws1.write(row, col + 11, tax_rate, line_content_style)
                ws1.write(row, col + 12, base_amount[0], line_content_style)
                ws1.write(row, col + 13, base_amount[2], line_content_style)
                ws1.write(row, col + 14, base_amount[3], line_content_style)
                ws1.write(row, col + 15, base_amount[4], line_content_style)
                ws1.write(row, col + 16, base_amount[1], line_content_style)
                ws1.write(row, col + 17, "", line_content_style)
                ws1.write(row, col + 18, "", line_content_style)
                ws1.write(row, col + 19, "", line_content_style)
                ws1.write(row, col + 20, "", line_content_style)
                ws1.write(row, col + 21, "", line_content_style)

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
        ws1.write_merge(row, row, 2, 6, "Summary For CDNUR(6C)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Note/Voucher Number", sub_header_style)
        ws1.write(row, col + 2, "Note/Voucher date", sub_header_style)
        ws1.write(row, col + 3, "Invoice/Advance Payment Voucher number", sub_header_style)
        ws1.write(row, col + 4, "Invoice/Advance Payment Voucher date", sub_header_style)
        ws1.write(row, col + 5, "Pre GST", sub_header_style)
        ws1.write(row, col + 6, "Document Typ", sub_header_style)
        ws1.write(row, col + 7, "Reason For Issuing document", sub_header_style)
        ws1.write(row, col + 8, "Supply Type", sub_header_style)
        ws1.write(row, col + 9, "Invoice Type", sub_header_style)
        ws1.write(row, col + 10, "Note/Voucher Value", sub_header_style)
        ws1.write(row, col + 11, "Rate", sub_header_style)
        ws1.write(row, col + 12, "Taxable Value", sub_header_style)
        ws1.write(row, col + 13, "Integrated Tax Paid", sub_header_style)
        ws1.write(row, col + 14, "Central Tax Paid", sub_header_style)
        ws1.write(row, col + 15, "State/UT Tax Paid", sub_header_style)
        ws1.write(row, col + 16, "Cess Paid", sub_header_style)
        ws1.write(row, col + 17, "Eligibility For ITC", sub_header_style)
        ws1.write(row, col + 18, "Availed ITC Integrated Tax", sub_header_style)
        ws1.write(row, col + 19, "Availed ITC Central Tax", sub_header_style)
        ws1.write(row, col + 20, "Availed ITC State/UT Tax", sub_header_style)
        ws1.write(row, col + 21, "Availed ITC Cess", sub_header_style)

        row += 1

        invoice_gst_tax_lines = {}

        igst = 0
        cgst = 0
        sgst = 0
        for invoice in self.refund_invoices.filtered(lambda p: not p.partner_id.x_gstin and p.company_id.state_id != p.partner_id.state_id \
                                                     and (p.amount_untaxed_signed * -1) > B2CL_INVOICE_AMT_LIMIT and p.type in ('in_refund', 'out_refund')):
            #Can't use invoice.tax_line_ids directly because it will contain on individual/leaf taxes (like CGST@2.5%, SGST@2.5%)
            #while gstr2 report needs the 'group' tax (like GST@5%).
            #Iterate through invoice.invoice_line_ids.invoice_line_tax_line_ids and collect/compute from there
            #for tax_line in invoice.tax_line_ids:
            _logger.info(invoice)
            grouped_tax_lines = {}
            for invoice_line in invoice.invoice_line_ids:
                if invoice_line.discount_amount and invoice_line.quantity != 0:
                    price = invoice_line.price_unit - (invoice_line.discount_amount / invoice_line.quantity)
                elif invoice_line.discount:
                    price = invoice_line.price_unit * (1 - (invoice_line.discount or 0.0) / 100.0)
                else:
                    price = invoice_line.price_unit

                if invoice_line.invoice_id.inclusive:
                    line_taxes = invoice_line.invoice_line_tax_ids.with_context(price_include=True,
                                                                                include_base_amount=True).compute_all_inc(
                        price,
                        invoice.currency_id,
                        invoice_line.quantity,
                        product=invoice_line.product_id,
                        partner=invoice.partner_id)
                else:
                    line_taxes = invoice_line.invoice_line_tax_ids.compute_all(price,
                                                                               invoice.currency_id,
                                                                               invoice_line.quantity,
                                                                               invoice_line.product_id,
                                                                               invoice.partner_id)

                # line_taxes = invoice_line.invoice_line_tax_ids.compute_all(invoice_line.price_unit, invoice.currency_id, invoice_line.quantity, invoice_line.product_id, invoice.partner_id)

                #_logger.info(line_taxes)
                for ln_tx in invoice_line.invoice_line_tax_ids: #.sorted(reverse=True):
                    gst_tax_id = None
                    # if ln_tx.gst_type in ('gst','ugst','igst'):
                    gst_tax_id = ln_tx
                    if grouped_tax_lines.get(ln_tx):
                        grouped_tax_lines[ln_tx][0] += line_taxes['total_excluded']
                    else:
                        grouped_tax_lines[ln_tx] = [0,0,0,0,0]  #[Taxable value, Cess amount, IGST, CGST, SGST]
                        grouped_tax_lines[ln_tx][0] = line_taxes['total_excluded']
                        #Collect the IGST/CGST/SGST breakup for this tax rate
                    for leaf_tax in line_taxes['taxes']:
                        if 'IGST' in leaf_tax['name']:
                            grouped_tax_lines[ln_tx][2] += leaf_tax['amount']
                        elif 'CGST' in leaf_tax['name']:
                            grouped_tax_lines[ln_tx][3] += leaf_tax['amount']
                        elif 'SGST' in leaf_tax['name'] or 'UTGST' in leaf_tax['name']:
                            grouped_tax_lines[ln_tx][4] += leaf_tax['amount']
                        else:       #CESS and other non-GST taxes
                            #TODO:Make the bold assumption that CESS is applied *after* GST taxes, so grouped_tax_lines[gst_tx_id] is already present
                            #Calculate CESS amount only
                            grouped_tax_lines[gst_tax_id][1] += sum(l['amount'] for l in line_taxes['taxes'] if 'GST' not in l['name'])

            invoice_gst_tax_lines[invoice] = grouped_tax_lines
            #_logger.info(grouped_tax_lines)


        for invoice, inv_tax_lines in sorted(invoice_gst_tax_lines.iteritems(), key=lambda p:(p[0].date, p[0].number)): # invoice_gst_tax_lines.items():
            for tax_id, base_amount in inv_tax_lines.items():
                #tax_id = self.env['account.tax'].browse(tax_id_id)

                for rateObj in tax_id:
                    if rateObj.amount_type == "group":
                        for childObj in rateObj.children_tax_ids:
                            tax_rate = childObj.amount * 2
                            break
                    else:
                        tax_rate = rateObj.amount

                    break
                # tax_rate = float( str(tax_id.name).split('@')[1].split('%')[0] )
                # if float_is_zero(tax_rate, precision_digits=3):     #Skip zero rated/exempted rates
                #     continue
                ws1.write(row, col + 1, invoice.number, line_content_style)
                ws1.write(row, col + 2, self.format_date(invoice.date_invoice), line_content_style)
                ws1.write(row, col + 3, invoice.refund_invoice_id.number, line_content_style)
                ws1.write(row, col + 4, self.format_date(invoice.refund_invoice_id.date_invoice), line_content_style)
                ws1.write(row, col + 5, "N", line_content_style)    #Pre-GST
                ws1.write(row, col + 6, invoice.type == 'in_refund' and "D" or "C", line_content_style)
                ws1.write(row, col + 7, invoice.name, line_content_style)
                ws1.write(row, col + 8, "TODO", line_content_style) #Supply-Type
                ws1.write(row, col + 9, "Regular", line_content_style)
                ws1.write(row, col + 10, invoice.amount_total, line_content_style)
                ws1.write(row, col + 11, tax_rate, line_content_style)
                ws1.write(row, col + 12, base_amount[0], line_content_style)
                ws1.write(row, col + 13, base_amount[2], line_content_style)
                ws1.write(row, col + 14, base_amount[3], line_content_style)
                ws1.write(row, col + 15, base_amount[4], line_content_style)
                ws1.write(row, col + 16, base_amount[1], line_content_style)
                ws1.write(row, col + 17, "", line_content_style)
                ws1.write(row, col + 18, "", line_content_style)
                ws1.write(row, col + 19, "", line_content_style)
                ws1.write(row, col + 20, "", line_content_style)
                ws1.write(row, col + 21, "", line_content_style)

                row += 1



    """ Utility to convert date/datetime to dd/mm/yyyy format """
    def format_date(self, date_in):
        return datetime.strftime(datetime.strptime(date_in, DEFAULT_SERVER_DATE_FORMAT), "%d/%m/%Y")
