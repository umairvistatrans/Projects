# -*- coding: utf-8 -*-


{
    'name': 'Point of Sale Spotii',
    'version': '1.0',
    'category': 'Sales/Point Of Sale',
    'summary': 'Spotii in the Point of Sale ',
    'description': """

This module allows the cashier to quickly give percentage-based
spotii to a customer.

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_spotii_views.xml',
        'views/res_config_settings_views.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'oe_pos_spotii/static/src/js/PaymentScreen.js',
        ],
    },

    "author": "Rinoy BR",
    'installable': True,
    'license': 'LGPL-3',
}
