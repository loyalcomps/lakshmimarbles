{
    'name': 'Negative Inventory Report ',
    'version': '10.0.2.0.0',
    'summary': "Negative Inventory Report",
    'category': 'Inventory',
    'author': 'Loyal IT Solutions',
    'company': 'Loyal IT Solutions',
    'website': 'http://www.loyalitsolutions.com',
    'description':'Negative Inventory Report',
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
        'views/qlty_inventory_pdf.xml',

    ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
