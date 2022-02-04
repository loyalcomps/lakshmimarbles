# -*- coding: utf-8 -*-
{
    'name': "internal_transfer_extended",

    'summary': """
        Additional fields like serial number,landing cost, MRP, selling price and multi barcode search option in internal transfer""",

    'description': """
        Additional fields like serial number,landing cost, MRP, selling price and multi barcode search option in internal transfer
    """,

    'author': "Loyal IT Solutions",
    'website': "http://www.loyalitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','pos_multi_barcodes'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}