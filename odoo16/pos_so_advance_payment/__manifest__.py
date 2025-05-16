# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software.
# See LICENSE file for full copyright & licensing details.

# Author: Aktiv Software PVT. LTD.
# mail:   odoo@aktivsoftware.com
# Copyright (C) 2015-Present Aktiv Software PVT. LTD.
# Contributions:
#           Aktiv Software:
#              - Aiendry Sarkar
#              - Heli Kantawala
#              - Saurabh Yadav
{
    'name': 'Create Sale Order, Delivery Address, Advance Payment from POS',
    'version': '16.0.1.0.0',
    'category': 'Hidden',
    'author': 'Aktiv Software',
    'summary': "Create Sale Order, Manage Delivery Address and Register Advance Payment from POS" ,
    'description': """Create Sale Order, Manage Delivery Address and Register Advance Payment from POS.""",
    'depends': ['point_of_sale', 'sale_management','web', 'pos_loyalty'],
    'price': 20.00,
    "license": "OPL-1",
    'currency': "EUR",
    'data': [
    'views/pos_views.xml',
    'views/sale_order_form.xml',
    'views/res_config_settings_view.xml'
    ],
    'installable': True,
    'auto_install': True,
    'assets': {
        'point_of_sale.assets': [
            'pos_so_advance_payment/static/src/css/pos_quote_button.css',
            'pos_so_advance_payment/static/src/js/pos_create_quotation_popup.js',
            'pos_so_advance_payment/static/src/js/pos_create_quote_button.js',
            'pos_so_advance_payment/static/src/js/create_complete_sale_order_popup.js',
            'pos_so_advance_payment/static/src/js/sale_order_bill_screen.js',
            'pos_so_advance_payment/static/src/xml/complete_sale_order_popup.xml',
            'pos_so_advance_payment/static/src/xml/pos_create_quote_button.xml',
            'pos_so_advance_payment/static/src/xml/sale_order_bill_screen.xml',
        ],
    },
    'images': [
        'static/description/banner.jpg'
    ],
    'installable': True,
    'auto_install': False,
    
}