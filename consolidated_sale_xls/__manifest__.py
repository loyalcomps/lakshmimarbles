{
    'name': 'Consolidated sale report',
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
                'point_of_sale'
                ],
    'data': [
        'views/wizard_view.xml',

        'views/sale_report_pdf.xml',

    ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'application':True,
    'installable': True,
    'auto_install': False,
}
