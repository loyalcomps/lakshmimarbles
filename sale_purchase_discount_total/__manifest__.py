# -*- coding: utf-8 -*-
{
    'name': "Discount to Total Amount in Sale & Purchase",

    'summary': """
        Discount to total amount in sale, purchase, customer invoice and vendor bill """,

    'description': """
        Discount to total amount in sale, purchase, customer invoice and vendor bill
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
    'depends': ['base','sale','purchase','account','purchase_expense_journal'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/purchase_view.xml',
        'views/res_config_view.xml',
        'views/account_invoice_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}