# -*- coding: utf-8 -*-

{
    'name': 'POS Receipt Customize',
    'summary': """POS Receipt""",
    'version': '16.0.1.0',
    'description': """POS Receipt""",
    'author': 'Mostafa Abbas',
    'category': 'Point of Sale',
    'depends': ['base', 'barcodes','product','point_of_sale'],
    'license': 'AGPL-3',
    'data': [
        'views/product_view.xml',
        'views/pos_config_view.xml',
        'views/res_config_settings_views.xml',
        'views/pos_order_line.xml',

    ],
    'demo': [],
    'assets': {
        'point_of_sale.assets': [
            'pos_receipt_customize/static/src/js/**/*.js',
            'pos_receipt_customize/static/src/xml/**/*.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
}
