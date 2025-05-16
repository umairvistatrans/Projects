# -*- coding: utf-8 -*-
{
    'name': "External E-commerce Integration",
    'summary': "Defines the rules of integration between 7md external website and odoo",
    'category': 'Extra',
    'version': '1.0',
    'depends': ['base', 'product', 'sale', 'app_product_brand', 'account'],
    'data': [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/res_company.xml",
        "views/stock_location.xml",
        "views/sync_model_view.xml",
        "views/sync_logs.xml",
        "views/account_move.xml",
        "views/report_invoice.xml",
        "wizard/sync_models_wiz_view.xml",
    ],
    'license': 'LGPL-3',
}
