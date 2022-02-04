# -*- coding: utf-8 -*-
{
    'name': "Cheque Management",

    'summary': """
        Allows to register supplier payment via cheque and manages full transaction process.""",

    'description': """
        Possible to transfer amount to an intermediate account. added new stages( for eg: Printed, Send for Approval, Approved,
         Send forSignature, Release, Cheque Cancellation etc) with proper authorization. Multi vendor bill payment is also possible.
    """,

    'author': "LOYAL IT SOLUTIONS",
    'website': "http://www.loyalitsolutions.com",
    'sequence' : 0,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_check_printing'],

    # always loaded
    'data': [
        'security/cheque_security.xml',
        'security/ir.model.access.csv',
        'data/account_data.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/account_invoice_view.xml',
        'views/account_config_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}