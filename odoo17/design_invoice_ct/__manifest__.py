# -*- coding: utf-8 -*-
{
    'name': "Sale Report",
    'version': '1.0',
    'summary': "Sale Report module",
    'description': "Sale Report module",
    'author': 'Caribou CS.',
    'company': 'Caribou CS.',
    'website': "https://www.cariboucs.com",
    'license': 'Other proprietary',
    'category': 'Sales',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sales_management_ct', 'sale_pdf_quote_builder'],
    # always loaded
    'data': [
        'report/order_report.xml',
        'report/reports.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
