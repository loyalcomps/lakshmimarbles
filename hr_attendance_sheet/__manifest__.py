# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Sheet And Policies",

    'summary': """Managing  Attendance Sheets for Employees
        """,

    'description': """
        
    """,

    'author': "Ramadan Khalil",
    'website': "rkhalil1990@gmail.com",
    'price': 99,
    'currency': 'EUR',

    'category': 'hr',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'hr',
                'hr_payroll',
                'hr_holidays',
                'hr_attendance'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/change_att_data_view.xml',
        'views/hr_attendance_sheet_view.xml',
        'views/hr_attendance_policy_view.xml',
        'wizard/change_att_data_view.xml',
        'data/hr_attendance_sheet_data.xml',
    ],
    'images': ['static/description/bannar.jpg'],

    'license': 'OPL-1',
    'demo': [
        'demo/demo.xml',
    ],
}
