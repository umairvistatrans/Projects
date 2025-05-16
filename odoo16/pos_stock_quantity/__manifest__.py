# -*- coding: utf-8 -*-
{
    'name': 'POS Stock',
    'version': '16.0.1.1',
    'category': 'Point Of Sale',
    'author': 'D.Jane',
    'sequence': 10,
    'summary': 'Display Stocks on POS Location. Update Real-Time Quantity Available.',
    'description': "",
    'depends': ['point_of_sale', 'stock'],
    'data': [
        'views/pos_config.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_stock_quantity/static/src/js/**/*.js',
            'pos_stock_quantity/static/src/xml/**/*.xml',
            "pos_stock_quantity/static/src/css/**/*.css",
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'currency': 'EUR',
}
