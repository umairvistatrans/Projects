# -*- coding: utf-8 -*-
{
    'name': 'Approval Matrix (Malex)',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'This application allows you to set Dynamic Approval Workflow on Submissions, Sales Orders, QC requests.',
    'description':
        """
This application allows you to set Dynamic Approval Workflow on Submissions, Sales Orders, QC requests.""",
    'author': 'Caribou CS.',
    'company': 'Caribou CS.',
    'website': "https://www.cariboucs.com",
    'license': 'Other proprietary',

    'depends': ['portal_management_mlx', 'sales_management_mlx'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'wizard/approval_refuse_view.xml',
        'views/submission_request_views.xml',
    ],
    'installable': True,
    'application': False,
}
