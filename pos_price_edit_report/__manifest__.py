# -*- coding: utf-8 -*-
{
    'name': "POS Price Edit Report",

    'summary': """
        Price edited POS bills report""",

    'description': """
        Price edited POS bills report
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
    'depends': ['base','pos_price_edit_log','point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/md_security.xml',
        'views/views.xml',
        'views/price_edit_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}