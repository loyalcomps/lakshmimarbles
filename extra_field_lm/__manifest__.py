# -*- coding: utf-8 -*-
{
    'name': "Extra Fields - Lakshmi",

    'summary': """
        Extra Fields like MRP,HSN to Product Master, PO, SO, Invoice & Vendor Bill""",

    'description': """
        Extra Fields like MRP,HSN to Product Master, PO, SO, Invoice & Vendor Bill. Allows to update these values to product master from vendor bill
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
    'depends': ['base','product','purchase','account','sale','gst_invoice','product_brand'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}