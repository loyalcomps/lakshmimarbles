# -*- coding: utf-8 -*-
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{
    'name': "TeXByte GST Solution",

    'summary': """
        Comprehensive GST software solution (India)""",

    'description': """
        GST tax rates, integrated HSN/SAC, Compliant Invoice print, GSTR1, GSTR2, GSTR2B returns etc.
        Commercial support separately available — contact TeXByte Solutions at <info@texbyte.in>
    """,

    'author': "TeXByte Solutions ʟʟᴘ",
    'website': "https://www.texbyte.in",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','product','sale_stock','account_accountant','purchase','account_tax_python','l10n_in'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/sales_line_view.xml',
        'views/purchase_line_view.xml',
        'views/invoice_line_view.xml',
        'views/invoice_supplier_view.xml',
        'views/account_tax_view.xml',
        'views/account_move_view.xml',
        'views/company_views.xml',
        'views/res_partner_views.xml',
        'views/res_country_view.xml',
        'views/stock_transfer_view.xml',
        'wizard/wizard_gst_reverse_charge_view.xml',
        'wizard/wizard_gst_invoice_gstr1_report_view.xml',
        'wizard/wizard_gst_invoice_gstr2_report_view.xml',
        'wizard/wizard_gst_invoice_gstr3b_report_view.xml',
        'reports/sale_invoice_report.xml',
        'reports/invoice_report.xml',
        'reports/billofsupply_report.xml',
        'reports/purchase_quotation_report.xml',
        'reports/purchase_order_report.xml',
        'reports/purchase_order_bi_report.xml',
        'reports/custom_report.xml',
        'reports/report_custom_filters.xml',
        'data/account.account.csv',
        'data/account.tax.csv',
        'data/texbyte_gst.hsncode.csv',
        'data/texbyte_gst.gstpos.csv',
        'data/res.country.state.csv',
        'data/product_product_discount_charges.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'installable':True,
    'application':True,
    'auto_install':False,
}
