# -*- coding: utf-8 -*-
{
    'name': "account_extended",

    'summary': """
        Extra features to basic account""",

    'description': """
        Extra features to basic account
    """,

    'author': "Loyal IT Solutions",
    'website': "http://www.loyalitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/brand_security.xml',
        'views/account_invoice_view.xml',
        'views/brand_view.xml',
        'views/res_config_view.xml',
	'views/barcode.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}