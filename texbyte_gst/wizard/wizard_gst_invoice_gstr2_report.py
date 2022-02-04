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

    _name = 'texbyte_gst.invoice.report.gstr2.wizard'

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
        self.refund_invoices = self.all_invoices.filtered(lambda i: i.state != 'cancel' and i.refund_invoice_id)  #Skip canceled refunds
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

        self.generate_b2b_report(xl_workbook)
        self.generate_b2bur_report(xl_workbook)
        self.generate_imps_report(xl_workbook)
        self.generate_impg_report(xl_workbook)
        self.generate_cdnr_report(xl_workbook)
        self.generate_cdnur_report(xl_workbook)
        self.generate_at_report(xl_workbook)
        self.generate_atadj_report(xl_workbook)
        self.generate_exempted_report(xl_workbook)
        self.generate_itcr_report(xl_workbook)
        self.generate_hsn_report(xl_workbook)


        xl_workbook.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name':'gstr2_'+str(from_date)+'-'+str(to_date)+'.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'texbyte_gst.invoice.report.gstr2.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    # Dont know the filter is correct in all report.
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
        ws1.write_merge(row, row, 2, 6, "Summary Of Supplies From Registered Suppliers B2B(3)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "GSTIN of Supplier", sub_header_style)
        ws1.write(row, col + 2, "Invoice Number", sub_header_style)
        ws1.write(row, col + 3, "Invoice Date", sub_header_style)
        ws1.write(row, col + 4, "Invoice Value", sub_header_style)
        ws1.write(row, col + 5, "Place of Supply", sub_header_style)
        ws1.write(row, col + 6, "Reverse Charge", sub_header_style)
        ws1.write(row, col + 7, "Invoice Type", sub_header_style)
        ws1.write(row, col + 8, "Rate", sub_header_style)
        ws1.write(row, col + 9, "Taxable Value", sub_header_style)
        ws1.write(row, col + 10, "Integrated Tax Paid", sub_header_style)
        ws1.write(row, col + 11, "Central Tax Paid", sub_header_style)
        ws1.write(row, col + 12, "State/UT Tax Paid", sub_header_style)
        ws1.write(row, col + 13, "Cess Paid", sub_header_style)
        ws1.write(row, col + 14, "Eligibility For ITC", sub_header_style)
        ws1.write(row, col + 15, "Availed ITC Integrated Tax", sub_header_style)
        ws1.write(row, col + 16, "Availed ITC Central Tax", sub_header_style)
        ws1.write(row, col + 17, "Availed ITC State/UT Tax", sub_header_style)
        ws1.write(row, col + 18, "Availed ITC Cess", sub_header_style)

        row += 1
        #variables for columns and totals

        invoice_gst_tax_lines = {}

        for invoice in self.sorted_invoices.filtered(lambda p: p.partner_id.vat and not p.refund_invoice_id): #GST registered customers
            #Can't use invoice.tax_line_ids directly because it will contain on individual/leaf taxes (like CGST@2.5%, SGST@2.5%)
            #while gstr2 report needs the 'group' tax (like GST@5%).
             #Iterate through invoice.invoice_line_ids.invoice_line_tax_line_ids and collect/compute from there
            #for tax_line in invoice.tax_line_ids:
            grouped_tax_lines = {}
#             igst_amount = invoice.tax_line_ids.filtered(lambda r: r.tax_id.gst_type == 'igst').amount
#             cgst_amount = invoice.tax_line_ids.filtered(lambda r: r.tax_id.gst_type == 'cgst').amount
#             sgst_amount = invoice.tax_line_ids.filtered(lambda r: r.tax_id.gst_type == 'sgst').amount
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

                    elif gst_tax_id:      #CESS and other non-GST taxes
                        #TODO:Make the bold assumption that CESS is applied *after* GST taxes, so grouped_tax_lines[gst_tx_id] is already present
                        #if len(grouped_tax_lines.get(ln_tx)) > 1:
                        #Calculate CESS amount only
                        grouped_tax_lines[gst_tax_id][1] += sum(l['amount'] for l in line_taxes['taxes'] if 'GST' not in l['name'])
                        #else:
                        #    grouped_tax_lines[ln_tx][1] = line_taxes['total_excluded']

            invoice_gst_tax_lines[invoice] = grouped_tax_lines

        for invoice, inv_tax_lines in sorted(invoice_gst_tax_lines.iteritems(), key=lambda p:(p[0].date, p[0].number)): # invoice_gst_tax_lines.items():
            for tax_id, base_amount in inv_tax_lines.items():
                #tax_id = self.env['account.tax'].browse(tax_id_id)
                #if tax_id.gst_type in ('gst','ugst','igst'):
                tax_rate = float( str(tax_id.name).split('@')[1].split('%')[0] )
                if float_is_zero(tax_rate, precision_digits=3):     #Skip zero rated/exempted rates
                    continue
                ws1.write(row, col + 1, invoice.partner_id.vat or "", line_content_style)
                ws1.write(row, col + 2, invoice.number, line_content_style)
                ws1.write(row, col + 3, self.format_date(invoice.date_invoice), line_content_style)
                ws1.write(row, col + 4, invoice.amount_total, line_content_style)
                ws1.write(row, col + 5, invoice.place_of_supply.name_get()[0][1], line_content_style)
                ws1.write(row, col + 6, invoice.reverse_charge and "Y" or "N", line_content_style)
                ws1.write(row, col + 7, "Regular", line_content_style)  #TODO: Invoice Type
                ws1.write(row, col + 8, tax_rate, line_content_style)
                ws1.write(row, col + 9, base_amount[0], line_content_style)
                ws1.write(row, col + 10, base_amount[2], line_content_style)
                ws1.write(row, col + 11, base_amount[3], line_content_style)
                ws1.write(row, col + 12, base_amount[4], line_content_style)
                ws1.write(row, col + 13, base_amount[1], line_content_style)
                ws1.write(row, col + 14, "NA", line_content_style)
                ws1.write(row, col + 15, 0, line_content_style)
                ws1.write(row, col + 16, 0, line_content_style)
                ws1.write(row, col + 17, 0, line_content_style)
                ws1.write(row, col + 18, 0, line_content_style)   #Cess amount

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

    """ B2BUR Summary Of Supplies From Unregistered Suppliers B2BUR(4B) """
    def generate_b2bur_report(self, wb1):
        #Error handling is not taken into consideraion
        self.ensure_one()

        ws1 = wb1.add_sheet('b2bur')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Summary Of Supplies From Unregistered Suppliers B2BUR(4B)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Supplier Name", sub_header_style)
        ws1.write(row, col + 2, "Invoice Number", sub_header_style)
        ws1.write(row, col + 3, "Invoice date", sub_header_style)
        ws1.write(row, col + 4, "Invoice Value", sub_header_style)
        ws1.write(row, col + 5, "Place Of Supply", sub_header_style)
        ws1.write(row, col + 6, "Supply Type", sub_header_style)
        ws1.write(row, col + 7, "Rate", sub_header_style)
        ws1.write(row, col + 8, "Taxable Value", sub_header_style)
        ws1.write(row, col + 9, "Integrated Tax Paid", sub_header_style)
        ws1.write(row, col + 10, "Central Tax Paid", sub_header_style)
        ws1.write(row, col + 11, "State/UT Tax Paid", sub_header_style)
        ws1.write(row, col + 12, "Cess Paid", sub_header_style)
        ws1.write(row, col + 13, "Eligibility For ITC", sub_header_style)
        ws1.write(row, col + 14, "Availed ITC Integrated Tax", sub_header_style)
        ws1.write(row, col + 15, "Availed ITC Central Tax", sub_header_style)
        ws1.write(row, col + 16, "Availed ITC State/UT Tax", sub_header_style)
        ws1.write(row, col + 17, "Availed ITC Cess", sub_header_style)

        row += 1

        invoice_gst_tax_lines = {}

        for invoice in self.sorted_invoices.filtered(lambda p: not p.partner_id.vat and not p.refund_invoice_id):   #Unregistered
            #Can't use invoice.tax_line_ids directly because it will contain on individual/leaf taxes (like CGST@2.5%, SGST@2.5%)
            #while gstr2 report needs the 'group' tax (like GST@5%).
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
                            grouped_tax_lines[ln_tx] = [0,0,0,0,0]  #[Taxable amount, Cess amount, IGST, CGST, SGST]
                            grouped_tax_lines[ln_tx][0] = line_taxes['total_excluded']
                        #Collect the IGST/CGST/SGST breakup for this tax rate
                        for leaf_tax in line_taxes['taxes']:
                            if 'IGST' in leaf_tax['name']:
                                 grouped_tax_lines[ln_tx][2] += leaf_tax['amount']
                            elif 'CGST' in leaf_tax['name']:
                                 grouped_tax_lines[ln_tx][3] += leaf_tax['amount']
                            elif 'SGST' in leaf_tax['name'] or 'UTGST' in leaf_tax['name']:
                                 grouped_tax_lines[ln_tx][4] += leaf_tax['amount']

                    elif gst_tax_id:       #CESS and other non-GST taxes
                        #TODO:Make the bold assumption that CESS is applied *after* GST taxes, so grouped_tax_lines[gst_tx_id] is already present
                        #if len(grouped_tax_lines.get(ln_tx)) > 1:
                        #Calculate CESS amount only
                        grouped_tax_lines[gst_tax_id][1] += sum(l['amount'] for l in line_taxes['taxes'] if 'GST' not in l['name'])
                        #else:
                        #    grouped_tax_lines[ln_tx][1] = line_taxes['total_excluded']

            invoice_gst_tax_lines[invoice] = grouped_tax_lines

        for invoice, inv_tax_lines in sorted(invoice_gst_tax_lines.iteritems(), key=lambda p:(p[0].date, p[0].number)): # invoice_gst_tax_lines.items():
            for tax_id, base_amount in inv_tax_lines.items():
                #tax_id = self.env['account.tax'].browse(tax_id_id)
                #if tax_id.gst_type in ('gst','ugst','igst'):
                tax_rate = float( str(tax_id.name).split('@')[1].split('%')[0] )
                if float_is_zero(tax_rate, precision_digits=3):     #Skip zero rated/exempted rates
                    continue
                ws1.write(row, col + 1, invoice.partner_id.vat or "", line_content_style)
                ws1.write(row, col + 2, invoice.number, line_content_style)
                ws1.write(row, col + 3, self.format_date(invoice.date_invoice), line_content_style)
                ws1.write(row, col + 4, invoice.amount_total, line_content_style)
                ws1.write(row, col + 5, invoice.place_of_supply.name_get()[0][1], line_content_style)
                ws1.write(row, col + 6, "Regular", line_content_style)  #TODO: Invoice Type
                ws1.write(row, col + 7, tax_rate, line_content_style)
                ws1.write(row, col + 8, base_amount[0], line_content_style)
                ws1.write(row, col + 9, base_amount[2], line_content_style)
                ws1.write(row, col + 10, base_amount[3], line_content_style)
                ws1.write(row, col + 11, base_amount[4], line_content_style)
                ws1.write(row, col + 12, base_amount[1], line_content_style)
                ws1.write(row, col + 13, "NA", line_content_style)
                ws1.write(row, col + 14, 0, line_content_style)
                ws1.write(row, col + 15, 0, line_content_style)
                ws1.write(row, col + 16, 0, line_content_style)
                ws1.write(row, col + 17, 0, line_content_style)   #Cess amount

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

    """ IMPS report """
    def generate_imps_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('imps')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Summary For IMPS (4C)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Invoice Number of Reg Recipient", sub_header_style)
        ws1.write(row, col + 2, "Invoice Date", sub_header_style)
        ws1.write(row, col + 3, "Invoice Value", sub_header_style)
        ws1.write(row, col + 4, "Place Of Supply", sub_header_style)
        ws1.write(row, col + 5, "Rate", sub_header_style)
        ws1.write(row, col + 6, "Taxable Value", sub_header_style)
        ws1.write(row, col + 7, "Integrated Tax Paid", sub_header_style)
        ws1.write(row, col + 8, "Cess Paid", sub_header_style)
        ws1.write(row, col + 9, "Eligibility For ITC", sub_header_style)
        ws1.write(row, col + 10, "Availed ITC Integrated Tax", sub_header_style)
        ws1.write(row, col + 11, "Availed ITC Cess", sub_header_style)

        row += 1

    """ IMPG report """
    def generate_impg_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('impg')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Summary For IMPG (5)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Port Code", sub_header_style)
        ws1.write(row, col + 2, "Bill Of Entry Number", sub_header_style)
        ws1.write(row, col + 3, "Bill Of Entry Date", sub_header_style)
        ws1.write(row, col + 4, "Bill Of Entry Value", sub_header_style)
        ws1.write(row, col + 5, "Document type", sub_header_style)
        ws1.write(row, col + 6, "GSTIN Of SEZ Supplier", sub_header_style)
        ws1.write(row, col + 7, "Rate", sub_header_style)
        ws1.write(row, col + 8, "Taxable Value", sub_header_style)
        ws1.write(row, col + 9, "Integrated Tax Paid", sub_header_style)
        ws1.write(row, col + 10, "Cess Paid", sub_header_style)
        ws1.write(row, col + 11, "Eligibility For ITC", sub_header_style)
        ws1.write(row, col + 12, "Availed ITC Integrated Tax", sub_header_style)
        ws1.write(row, col + 13, "Availed ITC Cess", sub_header_style)

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

        for invoice in self.refund_invoices.filtered(lambda p: p.partner_id.vat and \
                                                        p.type in ('in_refund','out_refund')): #GST registered customers
            #Can't use invoice.tax_line_ids directly because it will contain on individual/leaf taxes (like CGST@2.5%, SGST@2.5%)
            #while gstr2 report needs the 'group' tax (like GST@5%).
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
                            grouped_tax_lines[ln_tx] = [0,0,0,0,0]  #[Taxable amount, Cess amount, IGST, CGST, SGST]
                            grouped_tax_lines[ln_tx][0] = line_taxes['total_excluded']
                        for tax_line in line_taxes['taxes']:
                            if 'IGST' in tax_line['name']:
                                grouped_tax_lines[ln_tx][2] += tax_line['amount']
                            elif 'CGST' in tax_line['name']:
                                grouped_tax_lines[ln_tx][3] += tax_line['amount']
                            elif 'SGST' in tax_line['name'] or 'UTGST' in tax_line['name']:
                                grouped_tax_lines[ln_tx][4] += tax_line['amount']

                    elif gst_tax_id:       #CESS and other non-GST taxes
                        #TODO:Make the bold assumption that CESS is applied *after* GST taxes, so grouped_tax_lines[gst_tx_id] is already present
                        #Calculate CESS amount only
                        grouped_tax_lines[gst_tax_id][1] += sum(l['amount'] for l in line_taxes['taxes'] if 'GST' not in l['name'])

            invoice_gst_tax_lines[invoice] = grouped_tax_lines


        for invoice, inv_tax_lines in sorted(invoice_gst_tax_lines.iteritems(), key=lambda p:(p[0].date, p[0].number)): # invoice_gst_tax_lines.items():
            for tax_id, base_amount in inv_tax_lines.items():
                #tax_id = self.env['account.tax'].browse(tax_id_id)
                tax_rate = float( str(tax_id.name).split('@')[1].split('%')[0] )
                if float_is_zero(tax_rate, precision_digits=3):     #Skip zero rated/exempted rates
                    continue
                ws1.write(row, col + 1, invoice.partner_id.vat, line_content_style)
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


    """ AT report """
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
        ws1.write_merge(row, row, 2, 6, "Summary For  Tax Liability on Advance Paid  under reverse charge(10 A)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Place Of Supply", sub_header_style)
        ws1.write(row, col + 2, "Supply Type", sub_header_style)
        ws1.write(row, col + 3, "Gross Advance Paid", sub_header_style)
        ws1.write(row, col + 4, "Cess Amount", sub_header_style)

        row += 1


    """ ATADJ report """
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
        ws1.write_merge(row, row, 2, 6, "Summary For Adjustment of advance tax paid earlier for reverse charge supplies (10 B)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Place Of Supply", sub_header_style)
        ws1.write(row, col + 2, "Supply Type", sub_header_style)
        ws1.write(row, col + 3, "Gross Advance Paid to be Adjusted", sub_header_style)
        ws1.write(row, col + 4, "Cess Adjusted", sub_header_style)

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
        ws1.write_merge(row, row, 2, 6, "Summary For Composition, Nil rated, exempted and non GST inward supplies (7)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Description", sub_header_style)
        ws1.write(row, col + 2, "Composition taxable person", sub_header_style)
        ws1.write(row, col + 3, "Nil Rated Supplies", sub_header_style)
        ws1.write(row, col + 4, "Exempted (other than nil rated/non GST supply )", sub_header_style)
        ws1.write(row, col + 5, "Non-GST supplies", sub_header_style)

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
                    if taxes['taxes'] and  'GST' in taxes['taxes'][0]['name']:     #TODO: handle non-GST
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
                ws1.write(row, col+2, "")
                ws1.write(row, col+3, exemp_val['inter-state'][0])
                ws1.write(row, col+4, exemp_val['inter-state'][1])
                ws1.write(row, col+5, exemp_val['inter-state'][2])
                row += 1
                ws1.write(row, col+1, 'Intra-State supplies to registered persons')
                ws1.write(row, col+2, "")
                ws1.write(row, col+3, exemp_val['intra-state'][0])
                ws1.write(row, col+4, exemp_val['intra-state'][1])
                ws1.write(row, col+5, exemp_val['intra-state'][2])
            else:
                ws1.write(row, col+1, 'Inter-State supplies to unregistered persons')
                ws1.write(row, col+2, "")
                ws1.write(row, col+3, exemp_val['inter-state'][0])
                ws1.write(row, col+4, exemp_val['inter-state'][1])
                ws1.write(row, col+5, exemp_val['inter-state'][2])
                row += 1
                ws1.write(row, col+1, 'Intra-State supplies to unregistered persons')
                ws1.write(row, col+2, "")
                ws1.write(row, col+3, exemp_val['intra-state'][0])
                ws1.write(row, col+4, exemp_val['intra-state'][1])
                ws1.write(row, col+5, exemp_val['intra-state'][2])

            row += 1

    """ ITCR report """
    def generate_itcr_report(self, wb1):
        self.ensure_one()

        ws1 = wb1.add_sheet('itcr')

        # Content/Text style
        header_content_style = xlwt.easyxf("font: name Arial size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Arial size 10 px, bold 1, height 170; align: horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Arial size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Arial, height 170;")
        row = 1
        col = -1
        ws1.row(row).height = 500
        ws1.write_merge(row, row, 2, 6, "Summary Input Tax credit Reversal/Reclaim (11)", header_content_style)
        row += 2
        ws1.write(row, col + 1, "From:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_from), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "To:", sub_header_style)
        ws1.write(row, col + 2, self.format_date(self.date_to), sub_header_content_style)
        row += 1
        ws1.write(row, col + 1, "Description for reversal of ITC", sub_header_style)
        ws1.write(row, col + 2, "To be added or reduced from output liability", sub_header_style)
        ws1.write(row, col + 3, "ITC Integrated Tax Amount", sub_header_style)
        ws1.write(row, col + 4, "ITC Central Tax Amount", sub_header_style)
        ws1.write(row, col + 5, "ITC State/UT Tax Amount", sub_header_style)
        ws1.write(row, col + 6, "ITC Cess Amount", sub_header_style)

        row += 1

    """ HSN Summary """
    def generate_hsn_report(self, wb1):
        #Error handling is not taken into consideraion
        self.ensure_one()

        ws1 = wb1.add_sheet('hsnsum')
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
        ws1.write(row, col + 1, "HSN", sub_header_style)
        ws1.write(row, col + 2, "Description", sub_header_style)
        ws1.write(row, col + 3, "UQC", sub_header_style)
        ws1.write(row, col + 4, "Total Quantity", sub_header_style)
        ws1.write(row, col + 5, "Total Value", sub_header_style)
        ws1.write(row, col + 6, "Taxable Value", sub_header_style)
        ws1.write(row, col + 7, "Integrated Tax Amount", sub_header_style)
        ws1.write(row, col + 8, "Central Tax Amount", sub_header_style)
        ws1.write(row, col + 9, "State/UT Tax Amount", sub_header_style)
        ws1.write(row, col + 10, "Cess Amount", sub_header_style)

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
                    elif 'SGST' in tax_line['name'] or 'UTGST' in tax_line['name']:
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
        for invoice in self.refund_invoices.filtered(lambda p: not p.partner_id.vat and p.company_id.place_of_supply != p.place_of_supply \
                                                     and (p.amount_untaxed_signed * -1) > B2CL_INVOICE_AMT_LIMIT and p.type in ('in_refund', 'out_refund')):
            #Can't use invoice.tax_line_ids directly because it will contain on individual/leaf taxes (like CGST@2.5%, SGST@2.5%)
            #while gstr2 report needs the 'group' tax (like GST@5%).
            #Iterate through invoice.invoice_line_ids.invoice_line_tax_line_ids and collect/compute from there
            #for tax_line in invoice.tax_line_ids:
            _logger.info(invoice)
            grouped_tax_lines = {}
            for invoice_line in invoice.invoice_line_ids:
                line_taxes = invoice_line.invoice_line_tax_ids.compute_all(invoice_line.price_unit, invoice.currency_id, invoice_line.quantity, invoice_line.product_id, invoice.partner_id)
                #_logger.info(line_taxes)
                for ln_tx in invoice_line.invoice_line_tax_ids: #.sorted(reverse=True):
                    gst_tax_id = None
                    if ln_tx.gst_type in ('gst','ugst','igst'):
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
                if float_is_zero(tax_rate, precision_digits=3):     #Skip zero rated/exempted rates
                    continue
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

        ws1.write(row, col + 1, "Invoices for outward supply")
        ws1.write(row, col + 2, sorted_invs[0].number)
        ws1.write(row, col + 3, sorted_invs[-1].number)
        ws1.write(row, col + 4, len(sorted_invs))
        ws1.write(row, col + 5, len(self.caneceled_invoices)) #+ len(self.refund_invoices) + len(self.refunded_invoices))

    """ Utility to get integer present in a string """
    def get_num(self, x):
        return int( ''.join(ele for ele in x if ele.isdigit()))

    """ Utility to convert date/datetime to dd/mm/yyyy format """
    def format_date(self, date_in):
        return datetime.strftime(datetime.strptime(date_in, DEFAULT_SERVER_DATE_FORMAT), "%d/%m/%Y")
