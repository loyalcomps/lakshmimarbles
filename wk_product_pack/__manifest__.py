# -*- coding: utf-8 -*-
{
    'name': "wk_product_pack",

    'summary': """
        Combine two or more products together in order to create a bundle product.""",

    'description': """
        
    """,

    'author': "Webkul Software Pvt. Ltd.",
    'website': "http://www.webkul.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale','product','stock','sale_stock'],

    # always loaded
    'data': [
        'wizard/wk_product_pack_wizard.xml',
        'views/wk_product_pack_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images':['static/description/Banner.png']
}