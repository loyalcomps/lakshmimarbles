# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) BrowseInfo (http://browseinfo.in)
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
    'name' : "Send Customer Birthday Wishes",
    'version' : "1.0",
    'author' : "BrowseInfo",
    'summary': 'Send Birthday Greetings Email to Partner/Customer',
    'description' : '''
             Module to send an Email to customer on Birthday.
			send birthday wishes to customer, birthday wishes email to customer, Birthday Reminder email, Birthday Greetings email to customer. send birthday wishes to Partner, birthday wishes email to Partner, Birthday Reminder email, Birthday Greetings email to Partner. 
    ''',
    'license':'OPL-1',
    'category' : "Extra Tools",
    'data': [
             'res_partner_view.xml',
             'birthday_reminder_cron.xml',
             'edi/birthday_reminder_action_data.xml'
             ],
    'website': 'http://www.browseinfo.in',
    'depends' : ['sale'],
    'installable': True,
    'auto_install': False,
	"images":['static/description/Banner.png'],
}
