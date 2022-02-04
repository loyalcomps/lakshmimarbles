# -*- coding: utf-8 -*-
{
    'name': "Pos Combo Pack",

    'summary': """
        Module Which add the combo facility to add combo items to product""",

    'description': """
        
    """,

    'author': "LOYAL IT SOLUTIONS",
    'website': "http://www.loyalitsolutions.com",
    'sequence' : 0,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/combo.xml',
        'views/product.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/combo.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}