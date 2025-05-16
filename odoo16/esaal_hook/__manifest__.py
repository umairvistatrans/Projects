{
    'name': 'Esaal Odoo Plugin',
    'category': 'Sales/Point of Sale',
    'description': 'Esaal is a cutting-edge digital platform designed to revolutionize the way businesses and consumers manage receipts. By replacing traditional paper receipts with digital ones, Esaal offers a more sustainable, convenient, and enhanced shopping experience.',
    'summary': 'Esaal Point-Of-Sale Integration',
    'version': '1.0.0',
    'website': 'https://esaal.co/',
    'author': 'Esaal Technology Solutions',
    'images': ['static/description/banner.png'],
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/register.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'esaal_hook/static/src/xml/pos.xml',
            'esaal_hook/static/src/js/models.js'
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'uninstall_hook': 'uninstall_hook',
}
