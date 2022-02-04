{
    'name': 'Quality Super Bazar Sale Purchase Analysis',
    'version': '10.0.2.0.0',
    'summary': "Sale Purchase report",
    'category': 'Accounts',
    'author': 'Loyal IT Solutions',
    'company': 'Loyal IT Solutions',
    'website': 'http://www.loyalitsolutions.com',
    'depends': [
                'base',
                'account',
                'sale',
                'purchase',

                'point_of_sale',


                'report_xlsx'
                ],
    'data': [
            'views/wizard_view.xml',
        'views/salepurchase_report_pdf.xml',

    ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
