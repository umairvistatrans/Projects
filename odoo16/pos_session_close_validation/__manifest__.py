# -*- coding: utf-8 -*-
{
    'name': 'POS Session Close Validation',
    'version': '16.0.1',
    'category': 'Point Of Sale',
    'author': 'Oakland Odoo AE',
    'sequence': 10,
    'summary': 'Allow only Pos Manager to Close Pos Session.',
    'description': "Allow only Pos Manager to Close Pos Session.",
    'depends': ['point_of_sale', 'stock'],
    'assets': {
        'point_of_sale.assets': [
            'pos_session_close_validation/static/src/xml/**/*.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'currency': 'EUR',
}
