{
    'name': 'Quality Detailed Sale Report ',
    'version': '10.0.2.0.0',
    'summary': "POS Summary Detailed Report",
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
                'report_xlsx'
                ],
    'data': [
            'views/wizard_view.xml',
            'views/qlty_salesreport_pdf.xml',
            ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
