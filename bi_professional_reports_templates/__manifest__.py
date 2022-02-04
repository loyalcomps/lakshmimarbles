# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    'name': 'Odoo Professional Report Templates',
    'version': '2.0',
    'summary': 'Easily Customizable Report Template for Quotation/SO/Sales, Invoice, Picking/Delivery Order,RFQ/PO/Purchases',
    'category': 'Tools',
    'description': """
		Customize report, customize pdf report, customize template report, Customize Sales Order report,Customize Purchase Order report, Customize invoice report, Customize delivery Order report, Accounting Reports, Easy reports, Flexible report,Fancy Report template.
		
    """,
    'license':'OPL-1',
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'live_test_url':'https://youtu.be/_aihFWW4a5E',
    'depends': ['base', 'account', 'sale', 'purchase', 'stock', 'sale_stock', 'base_vat'],
    'data': [
		"res_company.xml",
		"invoice_report/fency_report_account.xml",
		"invoice_report/fency_report_invoice.xml",
		"invoice_report/report_invoice_classic.xml",
		"invoice_report/report_invoice_modern.xml",
"invoice_report/report_invoice_odoo_standard.xml",

"delivery_report/stock_report_classic.xml",
"delivery_report/fency_report_deliveryslip.xml",
"delivery_report/modern_report_deliveryslip.xml",
"delivery_report/odoo_standard_report_deliveryslip.xml",
"delivery_report/report_deliveryslip_classic.xml",

"purchase_report/classic_purchase_report.xml",
"purchase_report/classic_report_purchaseorder.xml",
"purchase_report/classic_report_purchasequotation.xml",
"purchase_report/fency_report_purchaseorder.xml",
"purchase_report/fency_report_purchasequotation.xml",
"purchase_report/modern_report_purchaseorder.xml",
"purchase_report/modern_report_purchasequotation.xml",
"purchase_report/odoo_standard_report_purchaseorder.xml",
"purchase_report/odoo_standard_report_purchasequotation.xml",

"sale_report/classic_sale_report.xml",
"sale_report/classic_report_saleorder.xml",
"sale_report/fency_report_saleorder.xml",
"sale_report/modern_report_saleorder.xml",
"sale_report/odoo_standard_report_saleorder.xml",
             ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}
