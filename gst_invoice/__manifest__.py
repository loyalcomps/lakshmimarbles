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

{
    'name'                  : 'GST - Returns and Invoices',
    'version'               : '1.0.0',
    'category'              : 'Accounting',
    'sequence'              : 1,
    "author"                :  "Webkul Software Pvt. Ltd.",
    "license"               :  "Other proprietary",
    'website'               : 'https://store.webkul.com/Odoo-GST-Invoices.html',
    'summary'               : 'GST Invoice Reports',
    "live_test_url"         : "http://odoo.webkul.com:8008/web?db=gst_invoice",
    'description'           : """

GST - Returns and Invoices
==========================

This Brilliant Module will generate csv. 
-------------------------------------------


Some of the brilliant feature of the module:
--------------------------------------------

	1. Export B2B csv.
	
	2. Export B2Cl csv.
	
	3. Export B2CS csv.
	
	4. Export HSN csv.
	
This module works very well with latest version of Odoo 10.0
--------------------------------------------------------------
    """,
    'depends': [
        'l10n_in',
        'account_tax_python',
    ],
    'data': [
        'data/ir_model_fields_data.xml',
        'data/port.code.csv',
        'data/data_unit_quantity_code.xml',
        'data/data_uom_mapping.xml',
        'data/data_dashboard.xml',
        'security/gst_security.xml',
        'security/ir.model.access.csv',
        'wizard/message_wizard_view.xml',
        'wizard/invoice_type_wizard_view.xml',
        'data/account_data.xml',
        'data/account_tax_data.xml',
        'data/account_fiscal_position_data.xml',
        'data/res_country_state_data.xml',
        'views/account_financial_report_data.xml',
        'views/account_report.xml',
        'views/product_template_view.xml',
        'views/report_invoice.xml',
        'views/report_templates.xml',
        'views/res_company_view.xml',
        'views/res_country_state_view.xml',
        'wizard/account_report_tax_payable_view.xml',
        'data/gob_server_actions.xml',
        'views/account_invoice_view.xml',
        'views/gst_view.xml',
        'views/port_code_view.xml',
        'views/gstr2_view.xml',
        'views/res_partner_views.xml',
        'views/gst_templates.xml',
        'views/gst_dashboard_view.xml',
        'views/account_fiscalyear_view.xml',
        'views/ir_attachment_view.xml',
        'views/account_period_view.xml',
        'views/gst_sequence.xml',
        'views/unit_quantity_code_view.xml',
        'views/uom_map_view.xml',
        'views/gst_action_view.xml',
        'views/gst_menu_view.xml'
    ],
    'sequence'      : 1,
    "images"        :  ['static/description/Banner.png'],
    'application'   : True,
    'installable'   : True,
    'auto_install'  : False,
    'price'         :  69,
    'currency'      :  'EUR',
    'pre_init_hook' :'pre_init_check',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
