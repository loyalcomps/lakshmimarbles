{
    'name': 'Quality Super Bazar Sale Purchase Analysis',
    'version': '10.0.2.0.0',
    'summary': "Sale Purchase Category Wise report",
    'category': 'Accounts',
    'author': 'Loyal IT Solutions',
    'company': 'Loyal IT Solutions',
    'website': 'http://www.loyalitsolutions.com',
    'depends': [
                'base',
                'account',

                'point_of_sale',


                'report_xlsx'
                ],
    'data': [
            'views/wizard_view.xml',
            ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
