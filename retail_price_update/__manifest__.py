# -*- coding: utf-8 -*-
{
    'name': "Retail Price Update",

    'summary': """
        Allows permitted users to update Retail Price based on product cost change""",

    'description': """
        Allows permitted users to update Retail Price based on product cost change of confirmed products.
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
    'depends': ['base','purchase','product','internal_transfer_extended','purchase_barcode','web_tree_dynamic_colored_field',
                'po_extra_features','update_product_price_change_fields'],

    # always loaded
    'data': [
        'security/price_change_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/sequence.xml',
        # 'views/cost_change_wizard.xml',
        # 'views/cost_changed_product_pdf.xml',
        'views/confirm_window_view.xml',
        # 'views/confirmed_product_wizard.xml',
        # 'views/confirmed_product_pdf.xml',
        # 'views/update_window_view.xml',
        # 'views/update_window_line_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}