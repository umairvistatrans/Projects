# This software and associated files (the “Software”) can only be used (executed)
# with a valid Numla Enterprise Subscription for the correct number of users.
# It is forbidden to modify, publish, distribute, sublicense,
# or sell copies of the Software or modified copies of the Software.
#
# See LICENSE for full licensing information.
# Copyright (c) 2021-2023 Numla Limited <az@numla.com>
# All rights reserved.
{
    'name': 'POS Sales Report',
    'description': 'Print POS Sales Report',
    'depends': ['base', 'point_of_sale'],
    'application': True,
    'version': '16.0',
    'license': 'AGPL-3',
    'installable': True,

    'data': [
        'security/ir.model.access.csv',
        'wizard/pos_sale_wizard.xml',
        # 'report/report.xml',
        'report/pos_sales_report.xml',
    ],
}

