# -*- coding: utf-8 -*-
{
    'name': 'OdooERP POS Product Availability By Location',
    'version': '16.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Product Availability',
    'depends': ['point_of_sale', 'stock'],
    'author': 'tou-odoo',
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'oe_pos_product_availability_by_location/static/src/scss/ProductAvailabilityButton.scss',
            'oe_pos_product_availability_by_location/static/src/css/**/*.css',
            'oe_pos_product_availability_by_location/static/src/js/**/*.js',
            'oe_pos_product_availability_by_location/static/src/xml/**/*.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'website': 'https://odooerp.ae/',
    'license': 'LGPL-3',
}
