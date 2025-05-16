# -*- coding: utf-8 -*-

{
    'name': 'POS Order List Screen Extension',
    'summary': """POS Order List Screen Extension""",
    'version': '16.0.1.0',
    'description': """POS Order List Screen Extension""",
    'author': 'Oakland Odoo AE',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'license': 'AGPL-3',
    'demo': [],
    'assets': {
        'point_of_sale.assets': [
            'pos_orderlist_screen_extension/static/src/js/**/*.js',
            'pos_orderlist_screen_extension/static/src/xml/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
}
