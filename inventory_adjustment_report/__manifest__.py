{
    'name': 'Inventory report ',
    'version': '10.0.2.0.0',
    'summary': "Inventory report",
    'description': """
       Inventory report
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
            'views/inv_report_pdf.xml',
            # 'views/print_negative_report.xml',
            ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
