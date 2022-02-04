# -*- coding: utf-8 -*-
{
    'name': "Tax Adjust",

    'summary': """The module allows to adjust the tax calculation in group of tax(incl) method
        """,

    'description': """
        To use go to Accounting --> TAX section, open tax edit form and move to "Advanced opitons" tab .
		  Please add adjust amount only for children tax
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
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}