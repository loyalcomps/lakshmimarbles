# -*- coding: utf-8 -*-
##############################################################################
#
#    Loyal IT Solutions Pvt. Ltd.
#    Copyright (C) 2017-TODAY Loyal IT Solutions(<http://www.loyalitsolutions.com>).
#    Author: Loyal IT Solutions(<http://www.loyalitsolutions.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'PDC Management',
    'version': '10.0.1.0',
    'author': 'Loyal IT Solutions, Shamnas',
    'company': 'Loyal IT Solutions',
    'website': 'http://www.loyalitsolutions.com',
    'category': 'Accounting',
    'summary': 'Extension on Cheques to handle Post Dated Cheques',
    'description': """ Extension on Cheques to handle Post Dated Cheques """,
    'depends': ['account_check_printing'],
    'data': [
        'data/account_pdc_data.xml',
        'views/account_payment_view.xml',
    ],
    'images': ['static/description/pdc_banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
