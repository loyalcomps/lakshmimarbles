# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Pos Options Bar',
    'version': '10.0.0.1.0',
    'category': 'Point Of Sale',
    'description': """
        Point Of Sale Options Bar Customized for Salon/Spa
    """,
    'sequence': 6,
    'summary': 'Touchscreen Interface for Shops',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'data': [
            'security/ir.model.access.csv',
            'view/templates.xml',
           ],
    'depends': ['point_of_sale'],
    'qweb': ['static/src/xml/pos_options.xml'],
    'installable': True,
    'auto_install': False,
    'price': 50,
    'currency': 'EUR',
}
