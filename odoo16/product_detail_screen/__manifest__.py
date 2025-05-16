# -*- coding: utf-8 -*-
{
    'name': "Product Detail Screen",
    'summary': """
        Data For Product Detail Screen
    """,
    'description': """
        Data For Product Detail Screen
    """,
    'author': "odooERP.AE",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', '7md_website', 'website_sale', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/views.xml',
        'views/comments.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'product_detail_screen/static/src/js/variant_mixin.js',
            'product_detail_screen/static/src/js/custom_js.js',
            'product_detail_screen/static/src/js/restrict_max_qty.js',
            "product_detail_screen/static/src/css/custom_css.css",
        ]}
}
