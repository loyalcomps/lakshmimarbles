# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Pos Backend Receipt',
    'version': '10.0.0.1.0',
    'category': 'Point Of Sale',
    'sequence': 6,
    'summary': 'Pos Receipt',
    'description': """Pos Receipt""",
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'data': [
            'views/templates.xml',
            'views/pos_backend_receipt_view.xml'
            ],
    'depends': ['point_of_sale'],
    'qweb': ['static/src/xml/pos_backend_receipt.xml'],
    'installable': True,
    'auto_install': False,
    'price': 30,
    'currency': 'EUR',
}
