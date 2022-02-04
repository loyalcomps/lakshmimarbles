{
    'name': 'Quality Super Bazar Sale Analysis',
    'version': '10.0.2.0.0',
    'summary': "Sale report",
    'category': 'Accounts',
    'author': 'Loyal IT Solutions',
    'company': 'Loyal IT Solutions',
    'website': 'http://www.loyalitsolutions.com',
    'depends': [
                'base',
                'account',
                'sale',
                'product',
                'point_of_sale',
                'stock',
                'purchase',


                'report_xlsx'
                ],
    'data': [
            'views/wizard_view.xml',
        'views/payment_report_pdf.xml',

    ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
