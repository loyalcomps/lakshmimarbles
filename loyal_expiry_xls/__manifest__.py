{
    'name': 'Expiry  report',
    'category': 'Account',
    'license': "AGPL-3",
    'summary': "Expiry report",
    'author': 'Loyal',
    'company': 'Loyal IT solutions',
    'website': 'http://www.loyalitsolutions.com',
    'depends': [
                'base',
                'account',
                'sale',
                'purchase',
                'report_xlsx'
                ],
    'data': [
            # 'security/ir.model.access.csv',
            'views/wizard_view.xml',
            'views/expiry_report_pdf.xml'
            ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'auto_install': False,
}
