# -*- coding: utf-8 -*-
{
    'name' : 'Odoo Top Trending Product Filters',
    'version' : '1.0',
    'summary': "Filter Inventory Valuation,Sale, Purchase, Customer, Supplier, Products",
    'sequence': 10,
    'description': """
Odoo Top Trending Products Filters
======================

Key Features
------------
* Top Trending Sold Product
* Top Trending Purchased Product
* Top Trending Sold & Purchased Product
* Top Trending Sold Product Variant
* Top Trending Purchased Product Variant
* Top Trending Sold & Purchased Product
* Filter Sale Quotation & Order Top Trending Sold Product
* Filter Purchase Quotation & Order Top Trending Purchased Product
* Filter Customer On Top Trending Sold Product
* Filter Supplier On Top Trending Purchased Product
* Filter Inventory Valuation On Top Trending Sold Product
* Filter Inventory Valuation On Top Trending Purchased Product
* Filter Inventory Valuation On Top Trending Sold & Purchased Product
""",
    'category': 'Sales',
    'author': 'Kalpesh Gajera',
    'website': 'www.visualcv.com/kalpesh-gajera',
    'depends' : ['sale', 'purchase', 'stock'],
    'data': [
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/product_view.xml',
        'views/res_partner_view.xml',
        'views/stock_view.xml',
        'data/top_most_trending_data_view.xml',
    ],
    'images': ['images/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
