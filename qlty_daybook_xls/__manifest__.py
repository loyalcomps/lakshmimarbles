{
    'name': 'Day Book For Excel',
    'version': '10.0.2.0.0',
    'summary': " Day Book Report ",
    'category': 'Accounts',
    'author': 'Loyal IT Solutions',
    'company': 'Loyal IT Solutions',
    'website': 'http://www.loyalitsolutions.com',
    'depends': [
                'base',
                'stock',
                'sale',
                'purchase',
                'report_xlsx',
                'account_report_menu',
                ],
    'data': [
            'views/wizard_view.xml',
            'views/daybook_report_pdf.xml',
            ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
