# -*- coding: utf-8 -*-
{
    'name': "Dynamic URL Data",
    'summary': """
        Dynamic Url Data for
        1: TOP setting
        2: NEW Arrival
        3: SALE (Discount)
    
    """,
    'description': """
        When you want the specified data Url must follow below pattern
        1: Top Selling ==> (http://localhost:8058/shop?top_selling=1)
        2: New Arrival ==> (http://localhost:8058/shop?new_arrival=1)
        3: Sale        ==> (http://localhost:8058/shop?sale=1)
    """,
    'author': "OdooERP.ae",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'website_sale', 'oe_login_signup'],
    'data': [
        'views/view.xml',
    ]

}
