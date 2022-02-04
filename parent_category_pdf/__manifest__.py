{
    'name': 'Category wise report ',
    'version': '10.0.2.0.0',
    'summary': "category report",
    'description': """
       category wise sale quantity and sale amount 
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
            'views/parent_category_pdf.xml',
            ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
