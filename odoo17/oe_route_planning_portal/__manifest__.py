# -*- coding: utf-8 -*-
{
    'name': "Oe Route Planning Portal",
    'author': 'Oakland',
    'website': 'https://www.odooerp.ae',
    'category': 'Uncategorized',
    'version': '17.0.0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'portal', 'project', 'oe_route_planning'],
    'data': [
        'security/app_security.xml',
        'security/ir.model.access.csv',
        'views/my_portal_view_template.xml',
        'views/my_portal_template_custom.xml',
        'views/res_users_form.xml',
        'views/templates.xml',
        'views/add_new_unplanned.xml',
        'views/new_product.xml',
        'views/new_customer.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'oe_route_planning_portal/static/src/css/project_portal.css',
            'oe_route_planning_portal/static/src/js/project.js',
            'oe_route_planning_portal/static/src/js/calendar-logics.js',
            'oe_route_planning_portal/static/src/js/calendar_navigations.js',
            'oe_route_planning_portal/static/src/js/portal_card_remove_class.js',
            'oe_route_planning_portal/static/src/js/add_unplanned_visit.js',
            'oe_route_planning_portal/static/src/js/add_new_product.js',
            'oe_route_planning_portal/static/src/js/add_new_customer.js',
        ],
    },
    'license': 'LGPL-3',
}
