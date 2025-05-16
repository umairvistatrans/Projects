# -*- coding: utf-8 -*-
{
    'name': "7md_website",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        this module is for 7md ecommerce store
    """,

    'author': "OAKLAND - odooERP.ae",
    'website': "http://www.odooerp.ae",


    'category': 'Uncategorized',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','website', 'website_sale', 'auth_oauth', 'website_sale_wishlist'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/website_menues.xml',
        'views/views.xml',
        'views/website_category_config.xml',
        'templates/header.xml',
        'templates/index.xml',
        'templates/about.xml',
        'templates/privacy_policy.xml',
        'templates/return_policy.xml',
        'templates/terms_and_conditions.xml',
        'templates/contact.xml',
        'templates/product_test_template.xml',
        'templates/credential_layout.xml',
        'templates/footer.xml',
        'templates/header_searchbar_custom.xml',
        # 'templates/product_details_screen.xml',
        'templates/pricelist_custom.xml',
        'templates/cart_custom_header.xml',
        'templates/cart_custom_header.xml',
        'templates/cart_customized_screen.xml',
        'templates/checkout_customized_screen.xml',
        # 'templates/shop_customized.xml',
        'templates/brand.xml',
        # 'templates/membership_screen.xml',
        'templates/home_categorytag_tabs.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
        'templates/shop_products.xml',
        'templates/shop_searchbar_custom.xml',
        'templates/wishlist.xml',
        'templates/template_user_subscription.xml',
        'templates/social_links.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_frontend':[
            "7md_website/static/src/js/js_add_cart_shop_json.js",
            "7md_website/static/src/js/landing.js",
            "7md_website/static/src/js/lightslider.js",
            "7md_website/static/src/css/lightslider.css",
            "7md_website/static/src/css/account.css",
            "7md_website/static/src/css/all.css",
            "7md_website/static/src/css/slick-theme.css",
            "7md_website/static/src/css/slick.css",
            "7md_website/static/src/css/bootstrap-grid.css",
            "7md_website/static/src/css/bootstrap-grid.rtl.css",
            "7md_website/static/src/css/bootstrap-reboot.css",
            "7md_website/static/src/css/bootstrap-reboot.rtl.css",
            "7md_website/static/src/css/bootstrap-utilities.css",
            "7md_website/static/src/css/bootstrap-utilities.rtl.css",
            "7md_website/static/src/css/bootstrap.css",
            "7md_website/static/src/css/bootstrap.rtl.css",
            "7md_website/static/src/css/layout-767.css",
            "7md_website/static/src/css/layout-992.css",
            # "7md_website/static/src/css/layout-ar.css",
            "7md_website/static/src/css/layout.css",
            "7md_website/static/src/css/main-page.css",
            "7md_website/static/src/css/product-details.css",
            "7md_website/static/src/css/shopping-cart.css",
            "7md_website/static/src/css/updated-styles.scss",
            "7md_website/static/src/css/product-details-custom.scss",
            "7md_website/static/src/css/cart_custom.scss",
            "7md_website/static/src/css/updated-styles-ar.scss",
            # "7md_website/static/src/js/bootstrap.bundle.min.js",
            # "7md_website/static/src/js/bootstrap.bundle.min.js.map",
            
            
            
        ],
    },
}
