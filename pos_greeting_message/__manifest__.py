# -*- coding: utf-8 -*-
{
    'name': "pos_greeting_message",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """

        boolean in point of sale ->configuration-> settings if it is true it will automatically
        to the all counters point of sale->configuration->point of sale
        if boolean is true it will display the meassge in print and bill print
       ( option for message display in print and bill print ).
       
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
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
'security/greetings.xml',
        'views/views.xml',
        'views/templates.xml',
'views/message.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}