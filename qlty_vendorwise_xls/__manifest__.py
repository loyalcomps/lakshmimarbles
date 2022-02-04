{
    'name': 'Quality Vendor Wise Profit And Loss  Report ',
    'version': '10.0.2.0.0',
    'summary': "Take Away Supermart Delivery report",
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
        'views/vendor_report_pdf.xml',

    ],
    'images': ['static/description/banner.jpg'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
