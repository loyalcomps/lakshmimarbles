# -*- coding: utf-8 -*-
{
    'name': "Accounting Extended",

    'summary': """
        Adds Brand,MRP,Category,Landing Castin PO, Vendor Bill
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Loyal IT Solutions",
    'website': "http://www.loyalitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','product','purchase'],

    # always loaded
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'security/brand_security.xml',
        'views/account_invoice_view.xml',
        'views/brand_view.xml',
        'views/barcode.xml',
        'views/res_config_view.xml',
        'views/templates.xml',
        'views/account_purchase.xml',
        'views/gst_invoice_template_report_id.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}