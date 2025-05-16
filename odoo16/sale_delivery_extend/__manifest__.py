# -*- coding: utf-8 -*-
{
    'name': 'Sale Delivery Extended',
    'version': '1.1',
    'category': 'Sale',
    'description': """
        Extend Delivery functions
    """,

    'depends': ['delivery', 'sale', 'purchase','external_commerce_integration','product','point_of_sale','mail'],
    'data': [
        
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/delivery_carrier_view.xml',
        'views/sale_order_view.xml',
        'views/stock_picking_view.xml',
        'views/shipping_order_mail_template.xml',
        'views/shipping_order.xml',
        'views/shipping_orders_details.xml',
        'views/product_view.xml',
        'views/pos_payment_method.xml',
    ],
}
