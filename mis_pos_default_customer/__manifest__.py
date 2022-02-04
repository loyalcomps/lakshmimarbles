# -*- coding: utf-8 -*-
###############################################################################
#
#    Mars IT Solutions.
#    Copyright (C) 2015-TODAY Mars IT Solution(<http://www.marsits.com>).
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
###############################################################################

{
    "name" : "POS - Default Customer",
    "description": """
            This module integrate to display default customer with image in POS.
    """,
    "version" : "10.0",
    "author" : "Mars IT Solution",
    "website": "http://www.marsits.com",
    "category" : "POS",
    "depends" : [
        'base', 'point_of_sale'
    ],
    "demo" : [],
    "data" : [
        'views/views.xml',
        'views/templates.xml',
    ],
    "qweb" : ["static/src/xml/*.xml"],
    "images": ['static/description/banner.png'],
    "installable" : True,
    "active" : False,
    "support" : "scrdhaduk@gmail.com",
    "price": "10",
    "currency": "EUR",
    "license": "OPL-1",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
