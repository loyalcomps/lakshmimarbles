# -*- coding: utf-8 -*-
{
    'name': "PO Extra Features",

    'summary': """
        Extra features like Total Discount,Margin,Margin discount, Margin Discount % and round off to Purchase Order,Stock""",

    'description': """
        Extra features like Total Discount,Margin,Margin discount, Margin Discount % and round off to Purchase Order,Stock
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
    'depends': ['base','purchase','accounting_extended','internal_transfer_extended'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/stock_view.xml',
        'views/invoice_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}