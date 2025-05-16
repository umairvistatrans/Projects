# -*- coding: utf-8 -*-
{
    'name': "Membership Subscription",
    'summary': """
        Membership Subscription
    """,
    'description': """
        Membership Subscription
    """,
    'author': "odooERP.ae",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', '7md_website', 'website_sale', 'website_sale_loyalty'],
    'data': [
        'security/ir.model.access.csv',
        'data/subscription_sequence.xml',
        'data/subscription_state_cron.xml',
        'views/views.xml',
        'views/subscriptions.xml',
        'views/templates.xml',
    ]
}
