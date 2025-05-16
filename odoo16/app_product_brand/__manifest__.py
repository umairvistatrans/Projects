{
    'name': 'Product Brand',
    'category': 'Product',
    'sequence': 2,
    'depends': [
        'sale',
    ],
    'summary': """
    Product brand manager
    """,
    'description': """    
     Product brand
    """,
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_brand_views.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
