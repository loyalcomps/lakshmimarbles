# -*- coding: utf-8 -*-
{
    'name': "report_general_ledger",

    'summary': """General Ledger Report""",

    'description': """
       General Ledger Report
    """,

    'author': "LOYAL IT SOLUTIONS",
    'website': "http://www.loyalitsolutions.com",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '10.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_report_menu'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_report.xml',
        'views/report_generalledger.xml',
        'wizard/account_report_common_view.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}