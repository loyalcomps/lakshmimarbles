{
    'name': 'Stock In Inventory',
    'version': '10.0.2.0.0',
    'summary': " Cash Flow  Report",
    'category': 'Warehouse',
    'author': 'Loyal IT Solutions',
    'company': 'Loyal IT Solutions',
    'website': 'http://www.loyalitsolutions.com',
    'depends': [
                'base',
                'stock',
                'stock_account',
                'report_xlsx',
        'account'
                ],
    'data': [
            'views/wizard_view.xml',
        'views/inventory_report_pdf.xml',

    ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
