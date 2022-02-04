# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2016 Shawn
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
    "name": "Inventory Stock Report",
    "version": "1.0",
    "author": "Ananthu Krishna",
    "license": "AGPL-3",
    "website": "www.codersfort.com",
    "summary": "Print pdf report by location",
    "description": "Print pdf report by location",
    "category": "Inventory",
    "depends": [
        'stock',
    ],
    "data": [
        "report/stock_inventory_report.xml",
        "report/stock_inventory_location_report.xml",
        "wizard/stock_quant_report.xml",
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {
        'python': [],
    },
}
