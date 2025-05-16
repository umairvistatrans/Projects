# -*- coding: utf-8 -*-
{
    'name': "Odoo REST API",
    'summary': """
        Odoo REST API""",
    'description': """
        Odoo REST API
    """,
    'category': 'developers',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
    'external_dependencies': {
        'python': ['pypeg2', 'requests']
    }
}