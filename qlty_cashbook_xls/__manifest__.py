{
    'name': 'Cash Book For Quality Excel',
    'version': '10.0.2.0.0',
    'summary': " Cash Flow  Report",
    'category': 'Warehouse',
    'author': 'Loyal IT Solutions',
    'company': 'Loyal IT Solutions',
    'sequence': 0,
    'website': 'http://www.loyalitsolutions.com',
    'depends': [
                'base',
                'stock',
                'sale',
                'purchase',
                'account',
                'report_xlsx',
                'account_report_menu'
                ],
    'data': [
            'views/wizard_view.xml',
            'views/cashbook_report_pdf.xml',
            ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'application':True,
    'installable': True,
    'auto_install': False,
}
