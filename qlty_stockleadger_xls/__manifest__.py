{
    'name': ' qlty_stockleadger_xls ',
    'version': '10.0.2.0.0',
    'summary': "",
    'category': 'Accounts',
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
                'report_xlsx',

                'point_of_sale',
                ],
    'data': [
            'views/wizard_view.xml',
            'views/stockleadger_report_pdf.xml',

            ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
