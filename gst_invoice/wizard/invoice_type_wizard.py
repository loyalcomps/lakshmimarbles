#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models

class InvoiceTypeWizard(models.TransientModel):
    _name = "invoice.type.wizard"

    invoice_type = fields.Selection([
                                ('b2b', 'B2B'),
                                ('b2cl', 'B2CL'),
                                ('b2cs', 'B2CS'),
                                ('export', 'Export')
                            ], string='Invoice Type', default='b2b')
    export = fields.Selection([
                                ('WPAY', 'WPay'),
                                ('WOPAY', 'WoPay')
                            ],
                            string='Export'
            )

    @api.model
    def updateInvoiceType(self):
        partial = self.create({})
        ctx = dict(self._context or {})
        return {'name': ("Bulk Action"),
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'invoice.type.wizard',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                'domain': '[]',
                }

    @api.multi
    def updateAccountInvoiceType(self):
        count = 0
        model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        invoice_type = self.invoice_type
        export = self.export
        for active_id in active_ids:
            invoiceObj = self.env[model].browse(active_id)
            invoiceObj.invoice_type = invoice_type
            if export:
                invoiceObj.export = export
            count = count + 1
        text = 'Invoice type of %s record has been successfully updated to %s.' % (
            count, invoice_type)
        partial = self.env['message.wizard'].create({'text': text})
        return {'name': ("Information"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'message.wizard',
                'view_id': self.env.ref('gst_invoice.message_wizard_form1').id,
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                }
