# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Pre-order Website",
    "version": "17.0.0.0",
    "category": "Website",
    'summary': 'Place PreOrder for Product Website Product Pre-Order Website Request to Purchase Product Shop Out of Stock Product E-commerce Pre-Order Product Website Customers Pre-Order Products on Web Store PreOrder Product Web Shop Product Request to Buy',
    "description": """Pre Order Website Product Odoo app is an innovative tool designed to enable businesses to offer pre-order functionality for their products through their website. This app allows businesses to accept pre-orders for products that are not yet available or are out of stock. User can configure and can set specific pre-order start and end dates, amount type, specify pre-order min-max quantities, send mail option, and custom messages. User can send email notifications to customers who have placed pre-orders automatically or manually, keeping them informed about the status of their orders and any updates regarding product availability or delivery timelines.""",
    "author": "BrowseInfo",
    'website': 'https://www.browseinfo.com',
    "price": 49,
    "currency": 'EUR',
    "depends": ['website', 'website_sale', 'sale', 'stock', 'sale_management', 'product_detail_screen'],
    "data": [

        'security/ir.model.access.csv',
        'data/ircron.xml',
        'data/preorder_notification_mail_template.xml',
        'views/sale_inherit_views.xml',
        'views/website_preorder_views.xml',
        'views/product_product_inherit.xml',
        'templates/portal_inherit_views.xml',
        # 'templates/website_sale_inherit_views.xml',

    ],
    'assets': {
        'web.assets_frontend': [
            'bi_website_preorder/static/src/js/website_preorder.js',
            'bi_website_preorder/static/src/js/websitesaledelivery.js',
            'bi_website_preorder/static/src/scss/website_preorder.scss',
        ],
    },
    'qweb': [],
    "license": 'OPL-1',
    "auto_install": False,
    "installable": True,
    'live_test_url': 'https://youtu.be/iFV6sgi9l_w',
    "images": ['static/description/Pre-order-Website-Banner.gif'],
}
