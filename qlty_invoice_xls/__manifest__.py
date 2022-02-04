{
    'name': 'Cash Book For Quality Excel',
    'version': '10.0.2.0.0',
    'summary': " Cash Flow  Report",
    'category': 'Warehouse',
    'author': 'Loyal IT Solutions',
    'company': 'Loyal IT Solutions',
    'website': 'http://www.loyalitsolutions.com',
    'depends': [
                'base',
                'stock',
                'sale',
                'purchase',
                'account',
                'report_xlsx'
                ],
    'data': [
            'views/wizard_view.xml',
        'views/invoice_report_pdf.xml',

    ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
