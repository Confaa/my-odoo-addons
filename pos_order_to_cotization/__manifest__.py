# -*- coding: utf-8 -*-
{
    'name': 'POS Customer Account to Sales',
    'version': '19.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Crea órdenes de venta desde POS cuando se usa Cuenta del Cliente',
    'description': """
        Este módulo genera automáticamente órdenes de venta cuando se realizan 
        pagos en el POS usando el método de pago "Cuenta del cliente".
        Permite al equipo de ventas gestionar estas transacciones.
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
        'sale_management',
    ],
    'data': [
        'views/pos_order_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}