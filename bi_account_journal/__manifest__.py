# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Bassam Infotech LLP(<http://www.bassaminfotech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Account Journal',
    'version': '1.0',
    'category': 'Accounting',
    'author': "LOYAL IT SOLUTIONS",
    'website': "http://www.loyalitsolutions.com",
    'sequence': 15,
    'summary': 'Accounting Journal Module',
    'description': """Accounting Journal Module""",
    'depends': ['base','account'],
    'data': [   
    
              'views/account_journal_views.xml',
              'views/multi_account_journal_views.xml',
              'views/ir_sequence.xml',
              'security/ir.model.access.csv',
              'report/account_template.xml',
              'report/account_report.xml',
              'report/account_journal_report.xml',
    ],
    'demo': [],

}
