# -*- coding: utf-8 -*-
{
    'name': "Gross Profit Report",

    'summary': """
        Cost of goods report, which includes sale products cost and gross profit for a particular period of time,
         GP percentage,products below 0% GP, 5%GP and 10% GP.""",

    'description': """
        Long description of module's purpose
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
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/cog_report_pdf.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}