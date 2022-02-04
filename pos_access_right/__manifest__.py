# -*- coding: utf-8 -*-

{
    'name': "pos_access_right",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
        
        Restrict user wise cash discount,discount,price,line discount in pos
    """,

    'author': "LOYAL IT SOLUTIONS",
    'website': "http://www.loyalitsolutions.com",
    'sequence' : 0,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list


    # need to change the cash discount module id="cash_disc" and pos_discoint in id="pos_disc"
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','cash_discount','pos_discount'],

    'data': [
        # 'security/res_groups.yml',
        'static/src/xml/templates.xml',
        'views/views.xml',
    ],
    'demo': [
        # 'demo/res_groups.yml',
    ],
    'installable': True,
}
