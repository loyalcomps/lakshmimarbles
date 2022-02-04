# -*- coding: utf-8 -*-
{
    'name': "Purchase Expense",

    'summary': """
        User can choose whether to add expense to purchase total or not. Expense entry while validating bill""",

    'description': """
        User can choose whether to add expense to purchase total or not. Expense entry while validating bill
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
    'depends': ['base','purchase','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/expense_security.xml',
        'views/views.xml',
        'views/res_config_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}