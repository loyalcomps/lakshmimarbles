{
    'name': 'TAX report ',
    'version': '10.0.2.0.0',
    'summary': "category report",
    'description': """
       daily tax report
   """,

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
    'data': ['views/views.xml',
            'views/wizard_view.xml',
            'views/daily_report_pdf.xml',
            ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
