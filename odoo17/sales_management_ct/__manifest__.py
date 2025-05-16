# -*- coding: utf-8 -*-
{
    'name': 'Advanced Sales Management (Caesar Thobe)',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Manage and customize Thobe measurements and designs in the sales process, with automatic data population and PDF invoice printing.',
    'description': """
    The Sale Management Caesar module for Odoo enhances the sales order process for Caesar Thobe by allowing detailed input of product measurements and designs, automatically populating customer-specific default measurements, and generating measurement invoices in PDF format. It also ensures that any updates to measurements during the sales process are reflected in the customer's master data, maintaining accurate records for future orders.
""",
    'author': 'Caribou CS.',
    'company': 'Caribou CS.',
    'website': "https://www.cariboucs.com",
    'license': 'Other proprietary',

    'depends': ['base', 'mail', 'sale_management', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/ct_design_views.xml',
        'views/measurement_views.xml',
        'views/partner_views.xml',
        'views/company_views.xml',
        'views/product_views.xml',
        'views/sale_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sales_management_ct/static/scss/style.scss',
        ],
    },
    'installable': True,
    'application': True,
}
