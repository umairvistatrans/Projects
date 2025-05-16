# -*- coding: utf-8 -*-
{
    'name': 'pos_custom',
    'version': '1.1',
    'category': 'Point Of Sale',
    'description': """
        Limit Product Characters to 25 letter + variant Part 
    """,
    'depends': ['point_of_sale', 'product', 'account', 'pos_hr', 'pos_so_advance_payment'],
    'data': [
        'security/record_rules.xml',
        'views/product_product_form.xml',
        'views/stock_picking_form.xml',
        # 'views/asset.xml',

    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_custom/static/src/js/**/*.js',
            'pos_custom/static/src/xml/**/*.xml',
        ],
    },
}
