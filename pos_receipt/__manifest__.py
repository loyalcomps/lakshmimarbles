# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Pos Receipt',
    'version': '10.0.0.1.0',
    'category': 'Point Of Sale',
    'description': """
        Point Of Sale Receipt Customized for Salon/Spa
    """,
    'sequence': 6,
    'summary': 'Touchscreen Interface for Shops',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'data': [
            'security/pos_receipt_security.xml',
            'security/ir.model.access.csv',
            'view/templates.xml',
            'view/pos_receipt_view.xml',
            'view/kitchen_screen_data.xml',
           ],
    'depends': ['pos_options_bar','arabic_product'],
    'qweb': ['static/src/xml/pos_receipt.xml'],
    'installable': True,
    'auto_install': False,
    'price': 30,
    'currency': 'EUR',
}
