# -*- coding: utf-8 -*-
{
    'name': "Product Report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
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
    'depends': ['base','product','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/product_mrp.xml',
        'views/product_landing.xml',
        'views/product_barcode.xml',
        'views/product_novendortax.xml',
        'views/product_sellzero.xml',
        'views/product_notinpo.xml',
        'views/product_notequaltax.xml',
        'views/product_mrpsell.xml',
        'views/templates.xml',
        'wizard/product_mrpsale.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}