{
    'name': 'Dead stock',
    'version': '10.0.2.0.0',
    'summary': "  Report",
    'category': 'Warehouse',
    'author': 'Loyal IT Solutions',
    'company': 'Loyal IT Solutions',
    'website': 'http://www.loyalitsolutions.com',
    'depends': [
                'base',
                'account',
                'sale',
                'purchase',
                'stock',
                'product',
                'point_of_sale',

                'report_xlsx'
                ],
    'data': [
            'views/wizard_view.xml',
        'views/seven_deadstock_pdf.xml'
            ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
