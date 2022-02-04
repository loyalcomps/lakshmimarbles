# -*- coding: utf-8 -*-
{
    'name': "gstr3b_report",

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
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','sale_stock','account_accountant','purchase','account_tax_python','l10n_in'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/company_view.xml',
        'views/views.xml',
        # 'views/templates.xml',
        # 'views/invoice.xml',
        # 'views/purchase.xml',
        'views/partner.xml',
        # 'views/sales_line_view.xml',
        # 'data/gstr3b_report.gstpos.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}