# -*- coding: utf-8 -*-
{
    'name': "Vendor wise P & L Report",

    'summary': """
        Vendor Wise Profit and Loss Report""",

    'description': """
        Vendor Wise Profit and Loss Report
    """,

    'author': "Loyal IT Solutions",
    'website': "http://www.loyalitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','account','sale','purchase','stock','report_xlsx'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/vendorwise_pandl_pdf.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}