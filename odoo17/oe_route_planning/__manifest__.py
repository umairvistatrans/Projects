# -*- coding: utf-8 -*-
{
    # Information
    'name': 'OE Route Planning Custom',
    'version': '17.0.0.0',
    'category': '',
    # Authore
    'author': 'Oakland',
    'website': 'https://www.odooerp.ae',
    # Dependency
    'depends': ['oe_ands_base','calendar'],
    'data': [
        'security/visit_security.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/rank_master_views.xml',
        'views/oe_visits_views.xml',
        'views/route_master_views.xml',
        'wizard/cancel_remarks_views.xml',
        'wizard/oe_rescheduled_wizard_views.xml',
        'views/res_partner_view.xml',
        'views/oe_visit_planning_views.xml',
    ],

    # Other
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
