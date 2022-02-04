# -*- coding: utf-8 -*-
{
    'name': "buy3_get1",

    'summary': """
        Buy 3 Get 1 Offer""",

    'description': """
       Buy 3 Get 1 Offer
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
    'depends': ['base','product','point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'datas/product.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/pos_config.xml',

    ],
    'qweb': [
        'static/src/xml/promotion.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}