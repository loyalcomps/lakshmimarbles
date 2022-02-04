# -*- coding: utf-8 -*-
{
    'name': "Sale, Purchase - Discount ",

    'summary': """
        Discount % and amount in sale, purchase, invoice, vendor bill""",

    'description': """
         Discount % and amount in sale, purchase, invoice, vendor bill
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
    'depends': ['base','purchase','sale','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/purchase.xml',
        'views/invoice.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}